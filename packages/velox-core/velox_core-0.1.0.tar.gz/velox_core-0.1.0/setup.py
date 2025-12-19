from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="velox-core",
    version="0.1.0",
    author="Zied Boughdir",
    author_email="ZiedBoughdir@gmail.com",
    description="High-Performance Middleware Engine for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zinzied/velox-core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    include_package_data=True,
)
