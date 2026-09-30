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
    package_data={"odfuzz": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyyaml==5.4',
        'pyodata==1.7.0',
    ],
    tests_require=[
        'pytest>=7.1.2',
        'pytest-cov>=3.0.0',
        'codecov>=2.1.12',
        'pylint>=2.8.3',
        'flake8==3.8.4',
        'bandit>=1.7.0'
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
