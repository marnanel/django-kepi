import os
import re
from io import open
from setuptools import find_packages, setup

# much of this was cribbed from django_rest_framework

here = os.path.abspath(os.path.dirname(__file__))
README = open('README.md', 'r', encoding='utf-8').read()

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('django_kepi')

setup(
    name='kepi',
    version=version,
    url='https://gitlab.com/marnanel/kepi/',
    license='GPL-2',
    description='ActivityPub for Django',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Marnanel Thurman',
    author_email='marnanel@thurman.org.uk',
    packages=[
        'kepi',
        'django_kepi',
        'trilby_api',
        ],
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.0",
    #zip_safe=False,
    classifiers=[
        # XXX fixme
    ],
    entry_points = {
        'console_scripts': [
            'kepi=django_kepi.command_line:main',
            ],
        },
)

