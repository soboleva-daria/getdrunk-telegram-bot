#!/usr/bin/python3

import io
import os

from setuptools import find_packages, setup

NAME = 'get-drunk-telegram-bot'
DESCRIPTION = 'A bot that helps you to get drunk in a proper way.'
URL = 'https://github.com/soboleva-daria/getdrunk-telegram-bot/'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = "0.0.0"

with open('requirements.txt') as file:
    REQUIRED_BY_PATH = []
    REQUIRED = []
    for line in file:
        if line.startswith('-e'):
            REQUIRED_BY_PATH.append(line.split()[1])
        else:
            REQUIRED.append(line)

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    dependency_links=REQUIRED_BY_PATH,
    include_package_data=True,
    package_data={'get_drunk_telegram_bot': ['utils/*', 'images/*']},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
