
from setuptools import setup, find_packages

setup(
    name="save-to-excel",
    version="0.1.0",
    author="Your Name",
    author_email="your@email.com",
    description="Save MongoDB or list data to Excel using pandas",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "pandas",
        "openpyxl"
    ],
)
