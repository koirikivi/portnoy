from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='portnoy',
    version='0.0.0',
    url='https://github.com/koirikivi/portnoy.git',
    author='Rainer Koirikivi',
    author_email='rainer@koirikivi.fi',
    description="A bot that trades on alpaca.markets based on Dave Portnoy's tweets",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'alpaca-trade-api',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-watch',
            'flake8',
            #'mocktail',
            'pip-tools',
        ],
    },
)
