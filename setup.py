from setuptools import setup, find_packages

setup(
    name='odfuzz',
    version='0.9.1',
    license='Apache License Version 2.0',
    url='https://github.wdf.sap.corp/I342520/ODfuzz',
    author='Lubos Mjachky',
    author_email='lubos.mjachky@sap.com',
    description='Fuzzer for testing applications communicating via the OData protocol',
    packages=find_packages(exclude=['tests', 'restrictions']),
    zip_safe=False,
    install_requires=[
        'bs4>=0.0.1',
        'pytest>=3.5.0',
        'gevent>=1.2.2',
        'requests>=2.18.4',
        'pymongo>=3.6.1',
        'lxml>=3.7.3',
        'pyyaml>=3.13',
        'plotly>=3.2.0',
        'pandas>=0.23.4'
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
