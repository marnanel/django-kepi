import os
import re
from io import open
from setuptools import setup

# much of this was cribbed from django_rest_framework

here = os.path.abspath(os.path.dirname(__file__))
README = open('README.md', 'r', encoding='utf-8').read()

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('chapeau')

setup(
    name='chapeau',
    version=version,
    url='https://gitlab.com/marnanel/chapeau/',
    license='GPL-2',
    description='ActivityPub social media daemon',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Marnanel Thurman',
    author_email='marnanel@thurman.org.uk',
    packages=['chapeau'],
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.0",
    zip_safe=False, # for now, anyway
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Framework :: Django',
        'Topic :: Communications :: Conferencing',
    ],
    entry_points = {
        'console_scripts': [
            'chapeau=chapeau.kepi.command_line:main',
            ],
        },
)

