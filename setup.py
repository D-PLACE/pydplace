from setuptools import setup, find_packages


setup(
    name='pydplace',
    version='2.0.0',
    license='Apache 2.0',
    description='programmatic access to D-PLACE/dplace-data',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    author='Robert Forkel',
    author_email='forkel@shh.mpg.de',
    url='https://d-place.shh.mpg.de',
    keywords='data',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=[
        'attrs>=18.1',
        'clldutils>=2.5.1',
        'csvw>=1.4.2',
        'attrs>=17.3',
        'pyglottolog>=1.2.1',
        'python-nexus>=1.63',
        'pycldf>=1.0.6',
        'ete3>=3.0.0b34',
        #'pygdal>=1.11.3.3',
        #'fiona',
        #'shapely',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'mock',
            'pytest>=3.1',
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
