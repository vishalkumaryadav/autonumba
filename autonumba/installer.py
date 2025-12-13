import sys
import shutil
import subprocess
from pathlib import Path
from setuptools import setup, Extension
from Cython.Build import cythonize
import tempfile

def compile_all(path):
    subprocess.run([sys.executable, "-m", "compileall", str(path)], check=False)

def build_binary_module(py_file: Path, out_dir: Path):
    module_name = py_file.stem
    ext = Extension(
        name=module_name,
        sources=[str(py_file)],
    )
    tmp = tempfile.mkdtemp()
    setup(
        script_args=["build_ext", "--inplace", "--build-lib", str(out_dir)],
        ext_modules=cythonize([ext], quiet=True),
    )
    shutil.rmtree(tmp, ignore_errors=True)

def aot_compile_folder(folder: Path):
    folder = Path(folder)
    out_dir = folder / "__autonumba_bin__"
    out_dir.mkdir(exist_ok=True)
    for f in folder.rglob("*.py"):
        if "__pycache__" not in str(f):
            build_binary_module(f, out_dir)

def reinstall(name):
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", name])
    subprocess.run([sys.executable, "-m", "pip", "install", name])
    