from setuptools import find_packages, setup

import aims


setup(
    # info
    name='aims',
    description=aims.__doc__,
    license='MIT',

    # version
    version=aims.__version__,

    # author details
    author=aims.__author__,
    author_email=aims.__email__,

    # setup directories
    packages=find_packages(),

    # setup data
    package_data={
        '': ['*.ico', '*.css'],
    },

    # requires
    install_requires=[
        item.strip() for item in open('requirements.txt', 'r').readlines()
        if item.strip()
    ],
    python_requires='>=3.10',
)
