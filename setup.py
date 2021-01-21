

import os
import setuptools


with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as f:
    long_description = f.read()


setuptools.setup(
    name="glasswall",
    version="0.1.0",
    description="Glasswall Python Wrapper",
    long_description=long_description,
    author="AngusWR",
    author_email="aroberts@glasswallsolutions.com",
    # url="",  # TODO
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6",
)
