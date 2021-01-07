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
        'gevent==20.5.0',
        'greenlet==0.4.15',
        'requests==2.23.0',
        'pymongo==3.10.1',
        'lxml==4.6.2',
        'pyyaml==5.3.1',
        'python-dateutil==2.8.1',
        'pyodata==1.4.0',
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
