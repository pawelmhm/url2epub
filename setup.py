# -*- coding: utf-8 -*-
#!/usr/bin/python
from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name="url2epub",
    version="0.1",
    author='Pawel Miech',
    author_email='pawelmhm@gmail.com',
    maintainer='Pawel Miech',
    maintainer_email='pawelmhm@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['url2epub = url2epub.cmdline:execute']
    },
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'Twisted>=14.0.0',
        "lxml",
        "treq",
        "pyOpenSSL",
        "service_identity"
    ],
)
