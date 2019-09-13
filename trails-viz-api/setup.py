import setuptools

import trailsvizapi

with open('README.md', 'r') as readme:
    long_description = readme.read()

with open('requirements.txt', 'r') as req:
    requirements = req.readlines()


PACKAGE_NAME = 'trailsvizapi'
VERSION = trailsvizapi.__version__

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    intall_package_data=True,
    description='API to get trails data for visualization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ]
)
