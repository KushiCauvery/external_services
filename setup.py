from setuptools import setup

setup(
    name='external_services',
    version='0.1',
    packages=['external_services'],
    include_package_data=True,  # Ensure package data is included
    install_requires=[
        'shared_config',
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
