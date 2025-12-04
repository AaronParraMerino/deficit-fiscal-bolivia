# setup.py en la raíz del proyecto
from setuptools import setup, find_packages

setup(
    name="deficit-fiscal-bolivia",
    version="1.0.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "streamlit>=1.29.0",
        "matplotlib>=3.8.0",
        "scipy>=1.13.0",
        "plotly>=5.18.0",
    ],
)