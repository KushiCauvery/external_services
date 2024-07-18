"""
Setup script for the external_services package.
"""

from setuptools import setup, find_packages

setup(
    name='adapter',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,  
    install_requires=[
        'django',
        'djangorestframework',
        'pycryptodome',
        'django-environ',
        'pystache',
        'psycopg2',
        'xmltodict',
        'suds',
        'PyJWT',
        # Add any other dependencies as needed for the project
    ],
)
