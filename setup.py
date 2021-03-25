

import os
import setuptools


with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as f:
    long_description = f.read()


setuptools.setup(
    name="glasswall",
    description="Glasswall Python Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AngusWR",
    author_email="aroberts@glasswallsolutions.com",
    url="https://github.com/filetrust/glasswall-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6",
    include_package_data=True
)
