from setuptools import find_packages, setup

setup(
    name="flaskr",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
    ],
)

# see setup.py and setup.cfg in original repo for alternative
# way to declare this:
# https://github.com/pallets/flask/tree/main/examples/tutorial
