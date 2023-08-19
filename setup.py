from setuptools import setup, find_packages

from my_pip_package import __version__

# Extra requirements
extra_maps = [
    'Basemap',
]

extra_test = [
    *extra_math,
    'pytest>=4',
    'pytest-cov>=2',
]

extra_dev = [
    *extra_maps,
    *extra_test,
]

setup(
    name='hamhelper',
    version=__version__,
    description='some helpful tools I use in research and fun',

    url='https://github.com/Ham0osh/hamHelper',
    author='Hamish Johnson',
    author_email='hamish_johnson@sfu.ca',

    packages=find_packages(exclude=['tests', 'tests.*']),

    install_requires=[
        'numpy',
        'matplotlib',
    ],

    extras_require={
        'map': extra_map,
        'dev': extra_dev,
    },

    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)