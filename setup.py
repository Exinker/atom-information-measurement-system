from setuptools import find_packages, setup


setup(
    # info
    name='src',

    # setup directories
    packages=find_packages(),

    # setup data
    package_data={
        '': ['*.iso', '*.css'],
    },

    # requires
    install_requires=[
        item.strip() for item in open('requirements.txt', 'r').readlines()
        if item.strip()
    ],
    python_requires='>=3.10',
)
