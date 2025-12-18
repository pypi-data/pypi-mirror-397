# setup.py
from setuptools import setup, find_packages

setup(
    name='timeformatter_az',
    version='0.1.0',
    author='Eldar',
    author_email='eldar6251@gmail.com',
    description='MM:SS.ss formatında verilən vaxtı Azərbaycan dilində mətnə çevirən PyPI kitabxanası.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SizinGithubProfiliniz/timeformatter_az', # GitHub linkinizi qeyd edin
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.6',
)