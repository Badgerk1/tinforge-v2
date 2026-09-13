from setuptools import find_packages, setup

setup(
    name="tinforge-v2",
    version="0.1.0",
    description="Professional TIN generation and multi-format export engine",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26",
        "scipy>=1.11",
        "pdfplumber>=0.11",
        "lxml>=5.2",
    ],
)
