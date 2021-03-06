from setuptools import setup, find_packages


setup(
    name='pydplace',
    version='2.4.1.dev0',
    license='Apache 2.0',
    description='programmatic access to D-PLACE/dplace-data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='https://d-place.org',
    keywords='data',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        'pybtex<0.23; python_version < "3.6"',
        'pybtex; python_version > "3.5"',
        'attrs>=19.1',
        'clldutils>=3.5.0',
        'cldfcatalog',
        'csvw>=1.6',
        'pyglottolog>=3.0',
        'python-nexus>=1.63',
        'pycldf>=1.14',
        # ete3 doesn't install its dependencies properly, so we have to:
        'six',
        'numpy',
        'ete3>=3.1.2',
        #'pygdal>=1.11.3.3',
        #'fiona',
        #'shapely',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=5',
            'pytest-mock',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    entry_points={
        'console_scripts': [
            'dplace=pydplace.__main__:main',
        ]
    },
)
