from setuptools import find_packages, setup

from src import APPLICATION_DESCRIPTION, APPLICATION_VERSION, AUTHOR_EMAIL, AUTHOR_NAME


setup(
    # info
    name='src',
    description=APPLICATION_DESCRIPTION,
    license='MIT',

    # version
    version=APPLICATION_VERSION,

    # author details
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,

    # setup directories
    packages=find_packages(),

    # setup data
    package_data={
        '': ['*.iso', '*.css'],
    },

    # requires
    # install_requires=[
    #     item.strip() for item in open('requirements.txt', 'r').readlines()
    #     if item.strip()
    # ],
    python_requires='>=3.10',
)
