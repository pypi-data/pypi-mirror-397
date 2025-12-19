from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="peafowl-dox",
    version="0.3.1",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy>=2.2.6",
        "pillow>=11.1.0",
        "opencv-python>=4.8.0",
        "pymupdf>=1.23.0",
        "o365>=2.0.9",
    ],
    python_requires='>=3.8'
)