#!/usr/bin/env python

from setuptools import setup, find_packages

with open('LICENSE') as f:
    license = f.read()

setup(
    name='blfuzzy',
    version='1.0.0',
    description='Fuzzy inference engine',
    url='https://github.com/jcasse/fuzzy-inference-engine',
    author='Juan Casse',
    author_email='jcasse@gmail.ai',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'cycler==0.10.0',
        'decorator==4.1.2',
        'matplotlib==2.1.0',
        'networkx==2.0',
        'numpy==1.13.3',
        'pandas==0.21.0',
        'py==1.4.34',
        'pyparsing==2.2.0',
        'pytest==3.2.3',
        'python-dateutil==2.6.1',
        'pytz==2017.3',
        'PyYAML==3.12',
        'scikit-fuzzy==0.3.1',
        'scipy==1.0.0',
        'six==1.11.0',
        'xlrd==1.1.0'
    ],
    tests_require=[
        'pytest==3.2.3'
    ],
    zip_safe=False)
