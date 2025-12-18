from setuptools import setup, find_packages

setup(
    name='amancal',
    version='0.1.0',
    author='Pravish',
    author_email= "pravishsrivastava6@gmail.com",
    description='A package for advanced calendar functionalities',
    long_description=open('README.md', "r", encoding= "utf-8").read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'amancal=amancal.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ], 
    install_requires=[
        # List your package dependencies here
    ],
)