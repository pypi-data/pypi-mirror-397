from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="ImageDataSpliter",
    version="0.1.2",
    packages=find_packages(),
    author="Volodymyr",
    author_email="vova.dzimina@gmail.com",
    description="This utility splits an image dataset into train, validation, and test subsets while preserving the class folder structure.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)