from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="data-transfer-lib",
    version="0.1.3",
    author="llirikh",
    author_email="zhukov.kg@phystech.edu",
    description="Library for data transfer between databases using PySpark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llirkh/data_transfer_lib",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires= [
        "pyspark>=3.3.0",
    ]
)