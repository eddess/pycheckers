# -*- coding: utf-8 -*-
from __future__ import with_statement
from setuptools import setup

setup(
    name='pycheckers',
    version='1.0.0',
    description="Combined linter pep8 and pylint",
    long_description='Just uses pep8 and pylint',
    keywords='pycheckers',
    author='Eddy Essien',
    author_email='eddy.essien@gmail.com',
    url='http://www.google.ca',
    license='Expat license',
    py_modules=['pycheckers'],
    namespace_packages=[],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pep8',
        'pylint'
    ],
    entry_points={
        'console_scripts': [
            'pycheckers = pycheckers:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
