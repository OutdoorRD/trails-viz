from setuptools import setup

setup(
    name='trails_site',
    packages=['trails_site'],
    include_package_data=True,
    install_requires=[
        'flask==0.12.2',
        'pandas',
        'geopandas',
        'numpy'
    ],
)
