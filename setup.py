# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import versioneer


setup_requires = (
    'pytest-runner',
)

install_requires = (
)

tests_require = (
    'cnx-archive',
    'psycopg2',
    'pytest',
    'pytest-snapshot',
    'pytest-cov',
)

setup(
    name='cnx-transforms',
    version=versioneer.get_version(),
    author='Connexions team',
    author_email='info@cnx.org',
    url='https://github.com/openstax/cnx-transforms',
    license='LGPL, see also LICENSE.txt',
    setup_requires=setup_requires,
    cmdclass=versioneer.get_cmdclass(),
    install_requires=install_requires,
    tests_require=tests_require,
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
)
