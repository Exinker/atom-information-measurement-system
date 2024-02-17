from setuptools import setup, find_packages


install_requires = [
    item.strip() for item in open('requirements.txt', 'r').readlines()
    if item.strip()
]

setup(
	# info
    name='src',

	# setup directories
    packages=find_packages(),

	# setup data
    package_data = {
        '': ['*.iso', '*.css'],
    },

	# requires
    install_requires=install_requires,
    python_requires='>=3.10',

)
