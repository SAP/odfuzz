from setuptools import setup, find_packages
from pathlib import Path

version = Path('VERSION').read_text().strip()

setup(
    name='odfuzz',
    version=version,
    license='Apache License Version 2.0',
    url='https://github.com/SAP/odfuzz',
    author='Lubos Mjachky, Jakub Filak, Petr Hanak',
    author_email='jakub.filak@sap.com, petr.hanak@sap.com',
    description='Fuzzer for testing applications communicating via the OData protocol',
    packages=find_packages(exclude=['tests', 'restrictions']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'odfuzz = odfuzz.odfuzz:main'
        ]
    },
    zip_safe=False,
    install_requires=[
        'gevent>=1.2.2',
        'requests>=2.18.4',
        'pymongo>=3.6.1',
        'lxml>=3.7.3',
        'pyyaml>=3.13',
        'python-dateutil>=2.7.5',
        'pyodata>=1.2.3',
    ],
    tests_require=[
        'mongomock>=3.14.0',
        'pytest>=3.5.0',
        'pytest-cov>=2.7.1',
        'codecov>=2.0.15',
        'pylint>=1.2.1',
        'bandit>=1.6.2'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Testing'
    ]
)
