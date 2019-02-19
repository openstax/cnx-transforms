# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = (
    'rhaptos.cnxmlutils',
)

tests_require = (
    'cnx-archive',
    'psycopg2',
    'pytest',
    'pytest-cov',
)

setup(
    name='cnx-transforms',
    author='Connexions team',
    author_email='info@cnx.org',
    url='https://github.com/openstax/cnx-transforms',
    license='LGPL, see also LICENSE.txt',
    install_requires=install_requires,
    tests_require=tests_require,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
)
