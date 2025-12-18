#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include "magneto.h"

/* ============================================================================
 * DÉFINITION DE L'OBJET PYTHON : MagnetoPattern (Type Object)
 * ============================================================================ */

typedef struct {
    PyObject_HEAD
    MagnetoPattern c_pattern; // La structure C ultra-rapide
    uint64_t c_state;         // L'état persistant pour le streaming
    PyObject *pattern_str;    // Référence à la chaîne Python originale (pour la GC)
} MagnetoPatternObject;


/* --- 1. Méthode d'allocation et désallocation (new/dealloc) --- */

static PyObject *
MagnetoPattern_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    MagnetoPatternObject *self;

    self = (MagnetoPatternObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        // Initialiser l'état C (streaming) à zéro
        self->c_state = 0;
        self->pattern_str = NULL;
    }
    return (PyObject *)self;
}

static void
MagnetoPattern_dealloc(MagnetoPatternObject *self)
{
    Py_XDECREF(self->pattern_str); // Libérer la référence à la chaîne Python
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free(self); // Libérer la mémoire de l'objet lui-même
}

/* --- 2. Méthode d'initialisation (__init__) : Compilation --- */

static int
MagnetoPattern_init(MagnetoPatternObject *self, PyObject *args, PyObject *kwds)
{
    const char *pattern_c;
    PyObject *pattern_obj;
    long options_long = MAGNETO_OPTION_NONE;
    
    static char *kwlist[] = {"pattern", "options", NULL};
    
    // Récupère la chaîne de motif et les options (long = int Python)
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|l", kwlist,
                                     &pattern_obj, &options_long)) {
        return -1;
    }

    // Le motif doit être une chaîne
    if (!PyUnicode_Check(pattern_obj)) {
        PyErr_SetString(PyExc_TypeError, "Le motif doit être une chaîne (str).");
        return -1;
    }

    // Conversion de la chaîne Python en chaîne C (UTF-8)
    pattern_c = PyUnicode_AsUTF8(pattern_obj);
    if (pattern_c == NULL) {
        return -1; // Échec de la conversion
    }

    // Référence la chaîne Python pour que le GC ne la supprime pas
    Py_XDECREF(self->pattern_str);
    Py_INCREF(pattern_obj);
    self->pattern_str = pattern_obj;
    
    // Conversion des options
    uint8_t options = (uint8_t)options_long;

    // Appel de la fonction C magneto_compile
    MagnetoResult res = magneto_compile(&self->c_pattern, pattern_c, options);

    if (res != MAGNETO_OK) {
        // Gestion des erreurs de compilation C
        const char *err_msg = "Erreur de compilation inconnue.";
        switch (res) {
            case MAGNETO_ERR_PATTERN_TOO_LONG:
                err_msg = "Motif trop long (max 64 caractères).";
                break;
            case MAGNETO_ERR_PATTERN_EMPTY:
                err_msg = "Motif vide.";
                break;
            case MAGNETO_ERR_INVALID_OPTIONS:
                err_msg = "Options de compilation invalides.";
                break;
            default:
                break;
        }
        PyErr_SetString(PyExc_ValueError, err_msg);
        return -1;
    }

    return 0; // Succès
}

/* --- 3. Méthodes Python (Scanner, Count, Find_First) --- */

/**
 * @brief magneto.Pattern.scan(data, max_matches=1024)
 * Scanne un buffer et retourne une liste d'offsets.
 */
static PyObject *
MagnetoPattern_scan(MagnetoPatternObject *self, PyObject *args, PyObject *kwds)
{
    Py_buffer view;
    long max_matches = 1024;
    static char *kwlist[] = {"data", "max_matches", NULL};

    // Récupère le buffer de données (bytes, bytearray, memoryview)
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|l", kwlist, &view.obj, &max_matches)) {
        return NULL;
    }
    
    // Tente d'accéder aux données binaires du buffer Python
    if (PyObject_GetBuffer(view.obj, &view, PyBUF_SIMPLE) == -1) {
        return NULL;
    }

    // Limiter la taille du tableau de sortie
    size_t array_size = (size_t)max_matches;
    if (array_size == 0 || view.len == 0) {
        PyBuffer_Release(&view);
        return PyList_New(0);
    }
    
    // Allouer dynamiquement le tableau d'offsets C
    size_t *matches = PyMem_Malloc(array_size * sizeof(size_t));
    if (matches == NULL) {
        PyBuffer_Release(&view);
        return PyErr_NoMemory();
    }
    
    // Appel de la fonction C (streaming intégré)
    size_t found = magneto_scan(
        &self->c_pattern,
        (const char *)view.buf,
        (size_t)view.len,
        &self->c_state, // État persistant
        matches,
        array_size
    );
    
    PyBuffer_Release(&view); // Libère la référence au buffer Python

    // Convertir le tableau C en liste Python
    PyObject *result_list = PyList_New(found);
    if (result_list == NULL) {
        PyMem_Free(matches);
        return NULL;
    }
    
    for (size_t i = 0; i < found; i++) {
        // Convertir size_t en PyLong (int Python)
        PyObject *offset = PyLong_FromSize_t(matches[i]);
        if (offset == NULL) {
            Py_DECREF(result_list);
            PyMem_Free(matches);
            return NULL;
        }
        PyList_SET_ITEM(result_list, i, offset); // Utilisation rapide sans vérification
    }

    PyMem_Free(matches);
    return result_list;
}

/**
 * @brief magneto.Pattern.count(data)
 * Compte le nombre d'occurrences sans stocker les positions.
 */
static PyObject *
MagnetoPattern_count(MagnetoPatternObject *self, PyObject *args)
{
    Py_buffer view;

    if (!PyArg_ParseTuple(args, "O", &view.obj)) {
        return NULL;
    }
    if (PyObject_GetBuffer(view.obj, &view, PyBUF_SIMPLE) == -1) {
        return NULL;
    }

    if (view.len == 0) {
        PyBuffer_Release(&view);
        return PyLong_FromSize_t(0);
    }

    // Appel de magneto_count (utilise magneto_scan_core avec store_matches=0)
    size_t count = magneto_count(
        &self->c_pattern,
        (const char *)view.buf,
        (size_t)view.len,
        &self->c_state
    );

    PyBuffer_Release(&view);
    return PyLong_FromSize_t(count);
}

/**
 * @brief magneto.Pattern.find_first(data)
 * Retourne l'offset de la première occurrence ou None.
 */
static PyObject *
MagnetoPattern_find_first(MagnetoPatternObject *self, PyObject *args)
{
    Py_buffer view;

    if (!PyArg_ParseTuple(args, "O", &view.obj)) {
        return NULL;
    }
    if (PyObject_GetBuffer(view.obj, &view, PyBUF_SIMPLE) == -1) {
        return NULL;
    }

    size_t pos = SIZE_MAX;
    if (view.len > 0) {
        // Appel de magneto_find_first (arrêt rapide)
        pos = magneto_find_first(
            &self->c_pattern,
            (const char *)view.buf,
            (size_t)view.len,
            &self->c_state
        );
    }

    PyBuffer_Release(&view);
    
    if (pos == SIZE_MAX) {
        Py_RETURN_NONE; // Retourne None si non trouvé
    } else {
        return PyLong_FromSize_t(pos); // Retourne l'offset
    }
}

/**
 * @brief magneto.Pattern.reset_state()
 * Réinitialise l'état de streaming à zéro.
 */
static PyObject *
MagnetoPattern_reset_state(MagnetoPatternObject *self, PyObject *Py_UNUSED(ignored))
{
    self->c_state = 0;
    Py_RETURN_NONE;
}

/* --- 4. Getters (Accesseurs Python) --- */

static PyObject *
MagnetoPattern_get_state(MagnetoPatternObject *self, void *closure)
{
    return PyLong_FromUnsignedLongLong(self->c_state);
}

static PyObject *
MagnetoPattern_get_length(MagnetoPatternObject *self, void *closure)
{
    return PyLong_FromLong(self->c_pattern.length);
}

static PyObject *
MagnetoPattern_get_options(MagnetoPatternObject *self, void *closure)
{
    return PyLong_FromLong(self->c_pattern.options);
}


/* --- 5. Définition des méthodes et attributs pour le Type Python --- */

static PyMethodDef MagnetoPattern_methods[] = {
    {"scan", (PyCFunction)MagnetoPattern_scan, METH_VARARGS | METH_KEYWORDS,
     "Scanne le buffer de données et retourne une liste d'offsets (streaming activé)."},
    {"count", (PyCFunction)MagnetoPattern_count, METH_VARARGS,
     "Compte le nombre total d'occurrences (le plus rapide)."},
    {"find_first", (PyCFunction)MagnetoPattern_find_first, METH_VARARGS,
     "Trouve et retourne l'offset de la première occurrence, ou None."},
    {"reset_state", (PyCFunction)MagnetoPattern_reset_state, METH_NOARGS,
     "Réinitialise l'état interne pour recommencer la recherche à partir de zéro."},
    {NULL}  /* Sentinel */
};

static PyGetSetDef MagnetoPattern_getsetters[] = {
    {"state", (getter)MagnetoPattern_get_state, NULL, "État Bitap interne (pour le streaming).", NULL},
    {"length", (getter)MagnetoPattern_get_length, NULL, "Longueur du motif.", NULL},
    {"options", (getter)MagnetoPattern_get_options, NULL, "Options de compilation (insensible à la casse, etc.).", NULL},
    {NULL}  /* Sentinel */
};

static PyTypeObject MagnetoPatternType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "magneto.Pattern",
    .tp_doc = "Objet motif Magneto compilé pour la recherche ultra-rapide.",
    .tp_basicsize = sizeof(MagnetoPatternObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = MagnetoPattern_new,
    
    // *** CORRECTION MSVC ***
    // Remplacement des typedefs (init_descr, destructor) par des pointeurs
    // de fonction explicites pour la compatibilité Windows/MSVC.
    .tp_init = (int (*)(PyObject *, PyObject *, PyObject *))MagnetoPattern_init,
    .tp_dealloc = (void (*)(PyObject *))MagnetoPattern_dealloc,
    
    .tp_methods = MagnetoPattern_methods,
    .tp_getset = MagnetoPattern_getsetters,
};


/* ============================================================================
 * DÉFINITION DU MODULE PYTHON : magneto
 * ============================================================================ */

/* Déclaration des constantes pour le module Python */
static PyObject *
module_get_constants(void)
{
    PyObject *d = PyDict_New();
    
    PyDict_SetItemString(d, "OPTION_NONE", PyLong_FromLong(MAGNETO_OPTION_NONE));
    PyDict_SetItemString(d, "OPTION_CASE_INSENSITIVE", PyLong_FromLong(MAGNETO_OPTION_CASE_INSENSITIVE));
    PyDict_SetItemString(d, "OPTION_WHOLE_WORD", PyLong_FromLong(MAGNETO_OPTION_WHOLE_WORD));
    // NOTE: Il serait plus propre d'utiliser la version de magneto.h si elle était exportée,
    // mais "1.0.0" correspond à ce qui est défini dans setup.py et magneto.h.
    PyDict_SetItemString(d, "__version__", PyUnicode_FromString("1.0.0")); 

    return d;
}

static PyModuleDef magnetomodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "magneto",
    .m_doc = "Moteur de recherche de motifs binaire C ultra-rapide pour Python.",
    .m_size = -1, // Taille de l'état du module (-1 signifie pas d'état)
};

PyMODINIT_FUNC
PyInit_magneto(void)
{
    PyObject *m;

    // 1. Enregistre le Type MagnetoPattern
    if (PyType_Ready(&MagnetoPatternType) < 0)
        return NULL;

    // 2. Crée le module
    m = PyModule_Create(&magnetomodule);
    if (m == NULL)
        return NULL;

    // 3. Ajoute la classe Pattern au module
    Py_INCREF(&MagnetoPatternType);
    if (PyModule_AddObject(m, "Pattern", (PyObject *)&MagnetoPatternType) < 0) {
        Py_DECREF(&MagnetoPatternType);
        Py_DECREF(m);
        return NULL;
    }

    // 4. Ajoute les constantes (Options, Version)
    PyObject *constants = module_get_constants();
    if (constants != NULL) {
        // NOTE: Ajout direct dans le module au lieu d'un sous-dictionnaire
        PyModule_AddObject(m, "OPTION_NONE", PyDict_GetItemString(constants, "OPTION_NONE"));
        PyModule_AddObject(m, "OPTION_CASE_INSENSITIVE", PyDict_GetItemString(constants, "OPTION_CASE_INSENSITIVE"));
        PyModule_AddObject(m, "OPTION_WHOLE_WORD", PyDict_GetItemString(constants, "OPTION_WHOLE_WORD"));
        PyModule_AddObject(m, "__version__", PyDict_GetItemString(constants, "__version__"));
        Py_DECREF(constants); // Libérer le dictionnaire temporaire
    }
    
    return m;
}