import re

import setuptools


def read_file(path):
    with open(path, "r") as handle:
        return handle.read()


def read_version():
    try:
        s = read_file("VERSION")
        m = re.match(r"v(\d+\.\d+\.\d+(-.*)?)", s)
        return m.group(1)
    except FileNotFoundError:
        return "0.0.0"


long_description = read_file("docs/source/description.rst")
version = read_version()

setuptools.setup(
    name="curvaceous",
    description="""""",
    keywords="",
    long_description=long_description,
    include_package_data=True,
    version=version,
    url="https://gitlab.com/greenhousegroup/ai/libraries/curvaceous/",
    author="Greenhouse AI team",
    author_email="ai@greenhousegroup.com",
    package_dir={"curvaceous": "src/curvaceous"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["numpy>=2.3,<3", "ortools>=9.14.6206,<10", "pandas>=2.3.1,<3"],
    data_files=[(".", ["VERSION"])],
    packages=setuptools.find_packages("src"),
)
