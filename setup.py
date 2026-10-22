from setuptools import setup, find_packages

from hamhelper import __version__

# Extra requirements
extra_test = [
    'pytest>=4',
    'coverage',
]

extra_ci = [
    *extra_test,
    'python-coveralls',
]

extra_dev = [
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

    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',

    # docs/ holds the coverage badge and has an __init__.py; without excluding it pip installs a top level
    # 'docs' package next to hamhelper.
    packages=find_packages(exclude=['tests', 'tests.*', 'docs', 'docs.*']),
    # The matplotlib style files have to be in the wheel for plt.style.use('hamhelper.styles.hamStyle') to work.
    # styles/ has an __init__.py so it is an ordinary package: matplotlib looks dotted style names up through
    # importlib.resources, which is safest on the older Pythons when the folder is a regular package.
    package_data={'hamhelper.styles': ['*.mplstyle']},

    python_requires='>=3.8',

    install_requires=[
        'numpy',
        # colours.register_cmaps and HamColour use mpl.colormaps (added in matplotlib 3.5)
        'matplotlib>=3.5',
    ],

    extras_require={
        'dev': extra_dev,
    },

    classifiers=[
        'Framework :: Flake8',
        'Intended Audience :: Science/Research',
        'License :: Free for non-commercial use',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.14',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
