from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import os

# Function to safely check if Cython is installed
def has_cython():
    try:
        from Cython.Build import cythonize
        return True
    except ImportError:
        return False

# Define extensions for "Pro" modules that need obfuscation
extensions = []

if has_cython():
    from Cython.Build import cythonize
    
    # List of modules to compile to binary
    # We will compile the core coordinator and licensing logic
    modules_to_compile = [
        "upif/core/coordinator.py",
        "upif/core/licensing.py",
        "upif/modules/neural_guard.py",
        "upif/integrations/openai.py",
        "upif/integrations/langchain.py"
    ]
    
    # Only try to compile if files exist
    existing_modules = [m for m in modules_to_compile if os.path.exists(m)]
    
    if existing_modules:
        extensions = cythonize(
            existing_modules,
            compiler_directives={'language_level': "3"}
        )

setup(
    ext_modules=extensions,
    entry_points={
        "console_scripts": [
            "upif=upif.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
