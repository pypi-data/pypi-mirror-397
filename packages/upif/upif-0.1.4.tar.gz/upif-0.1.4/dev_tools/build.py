import os
import shutil
import subprocess
import sys

def clean():
    """Removes previous build artifacts."""
    for d in ["build", "dist", "upif.egg-info"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    print("Cleaned build directories.")

def build():
    """Runs the setup.py build command."""
    print("Starting build process (Cython -> Wheel)...")
    try:
        # Run setup.py bdist_wheel
        subprocess.check_call([sys.executable, "setup.py", "build_ext", "--inplace"])
        subprocess.check_call([sys.executable, "setup.py", "bdist_wheel"])
        print("\nSUCCESS: Wheel created in dist/")
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Build failed: {e}")
        print("Note: You need a C compiler (MSVC on Windows, GCC on Linux) for Cython.")

def main():
    clean()
    build()

if __name__ == "__main__":
    main()
