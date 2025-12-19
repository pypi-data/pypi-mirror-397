from setuptools import setup, find_packages

setup(
    name='kd_simulator',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
    ],
)