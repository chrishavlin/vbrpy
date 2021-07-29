import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vbrpy",
    version="0.0.1",
    author="Chris Havlin",
    description="Generate VBRc boxes from python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"vbrpy": "vbrpy"},
    packages=setuptools.find_packages(where="vbrpy"),
    python_requires=">=3.9",
)

