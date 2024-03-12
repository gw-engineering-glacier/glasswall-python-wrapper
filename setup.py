

import os
import setuptools

current_directory = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(current_directory, "README.md")
with open(readme_path, "r", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="glasswall",
    description="Glasswall Python Wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AngusWR",
    author_email="aroberts@glasswall.com",
    url="https://github.com/gw-engineering/glasswall-python-wrapper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "lxml>=4.9.4,<5",
        "psutil>=5.9.8,<6",
    ],
)
