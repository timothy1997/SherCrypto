from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name = 'SherCrypto',

    version = '0.1',

    description = 'Python Console Cryptography Tool',

    url = 'github.com/timothy1997/SherCrypto',

    author = 'Timothy Sherry',
    author_email = 'timsherry97@gmail.com',

    license='MIT',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Cryptography Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5.2',
    ],

    keywords = ['Python', 'Encryption', 'Decryption', 'Cryptography', 'Tool', 'AES', 'Advanced', 'Encryption', 'Standard'],

    packages = ['SherCrypto'],

    install_requires=['pycrypto'],

    entry_points={
        'console_scripts': [
            'SherCrypto = SherCrypto.SherCrypto:main',
        ],
    }
)
