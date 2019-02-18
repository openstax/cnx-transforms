# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = (
    'rhaptos.cnxmlutils',
)

setup(
    name='cnx-transforms',
    author='Connexions team',
    author_email='info@cnx.org',
    url='https://github.com/openstax/cnx-transforms',
    license='LGPL, see also LICENSE.txt',
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
)
