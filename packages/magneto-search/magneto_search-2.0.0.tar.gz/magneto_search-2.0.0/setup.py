import os
import platform
from setuptools import setup, Extension

# ============================================================
# 1. OPTIONS DE COMPILATION (PORTABLES + HAUTE PERFORMANCE)
# ============================================================

compile_args = []

system = platform.system()

if system == 'Windows':
    # MSVC (Visual Studio)
    compile_args += [
        '/O2',  # Optimisation maximale MSVC
    ]
else:
    # GCC / Clang (Linux, macOS)
    compile_args += [
        '-O3',      # Optimisation maximale
        '-Wall',
        '-Wextra',
        '-std=c99',
    ]

    # --------------------------------------------------------
    # OPTIMISATION CPU AVANCÉE (OPTIONNELLE)
    # --------------------------------------------------------
    if os.environ.get('MAGNETO_NATIVE') == '1':
        compile_args.append('-march=native')

# ============================================================
# 2. EXTENSION C
# ============================================================

# Dans la section 2. EXTENSION C de votre setup.py:

magneto_extension = Extension(
    name='magneto',
    sources=[
        'magneto.c',
        'magneto_py_module.c',
        # RETIRER 'magneto.h' d'ici
    ],
    # GARDEZ CETTE LIGNE (include_dirs) pour aider le compilateur
    include_dirs=['.'], 
    extra_compile_args=compile_args,
)

# ============================================================
# 3. SETUP
# ============================================================

setup(
    name='magneto-search', # AJOUTER TEST
    version='2.0.0',            # Nouvelle version
    description='Ultra-fast binary pattern search engine (Bitap) written in C for Python.',
    long_description=(
        'Magneto is a high-performance C extension implementing a binary Bitap '
        'pattern matching engine. It is designed for real-time log analysis, '
        'binary scanning, and large-scale text processing where traditional '
        'regular expressions are too slow.'
    ),
    author='Votre Nom',
    author_email='votre@email.com',
    url='https://github.com/pirata-winox/magneto', 
    license='MIT',

    ext_modules=[magneto_extension],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        # CORRECTION : Remplacement du classificateur invalide
        'Topic :: Software Development :: Libraries :: Python Modules', 
        'Topic :: Text Processing', # Classificateur parent conservé
        'Topic :: Text Processing :: Indexing', # Optionnel, plus spécifique que 'Search'
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],

    keywords='bitap bitmask search c-extension performance logs streaming',
)