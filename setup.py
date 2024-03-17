from setuptools import setup, find_packages

from hamhelper import __version__

# Extra requirements
extra_maps = [
    'Basemap',
]

extra_test = [
    *extra_maps,
    'pytest>=4',
    'pytest-cov>=2',
]

extra_ci = [
    *extra_test,
    'python-coveralls',
]

extra_dev = [
    *extra_maps,
    *extra_test,
]

setup(
    name='hamhelper',
    version=__version__,
    description='Some helpful tools I use in research and fun. Primarily\
                 targeted to data visualization and pretty colours.',

    url='https://github.com/Ham0osh/hamHelper',
    author='Hamish Johnson',
    author_email='hamish_johnson@sfu.ca',

    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    packages=find_packages(exclude=['tests', 'tests.*']),

    install_requires=[
        'numpy',
        'matplotlib',
    ],

    extras_require={
        'map': extra_maps,
        'dev': extra_dev,
    },

    classifiers=[
        'Framework :: Flake8',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
