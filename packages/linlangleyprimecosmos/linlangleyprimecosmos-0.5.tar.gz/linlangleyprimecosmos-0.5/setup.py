import setuptools
from pathlib import Path

def read_requirements(filename="requirements.txt"):
    return [
        line.strip()
        for line in Path(filename).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setuptools.setup(
    # project information
    name='linlangleyprimecosmos', # project name, a unique name for PyPI, used for pip install/uninstall
    version='0.5',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Demo for building a Python project',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='Lin Chen',
    author_email='lin.chen@ieee.org',
    url='http://lin-chen-langley.github.io',
    project_urls = {
        'PyPI': 'https://pypi.org/manage/project/linlangleyprime/releases/',
        'Conda': 'https://anaconda.org/linchenVA/linlangleyprime'
        },

    # python versions
    python_requires=">=3.9",

    # package
    package_dir={'':'src'}, # location to find the packages
    packages=setuptools.find_packages(where="src"),
    # packages=['primepackage', ], # specify packages will be installed, used for import

    # executable script
    entry_points={
        "console_scripts": [
            "primegen = primepackage.generator:main",
        ]
    },

    # dependencies
    install_requires=read_requirements(),

    # test, build, publish
    extras_require = {
        "test": ["pytest", "pytest-cov"], # install pytest and pytest-cov
        "build": ["build"], # install build
        "publish": ["twine"] # install twine
        },

    # standardized metadata tags
    classifiers=[ # list of classifiers at https://pypi.org/pypi?%3Aaction=list_classifiers
      'Development Status :: 4 - Beta',
      'Environment :: X11 Applications :: GTK',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python',
      'Topic :: Desktop Environment',
      'Topic :: Text Processing :: Fonts'
      ],
)
