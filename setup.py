#!/usr/bin/env python

# Use 'distribute', a fork of 'setuptools'.
# This seems to be the recommended tool until 'distutils2' is completed.
# See: http://pypi.python.org/pypi/distribute

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Find the version from the package metadata.

import os
import re

package_version = re.search(
    "__version__ = '([^']+)'",
    open(os.path.join('spyral', '__init__.py')).read()).group(1)

# Resources
# - package_data is what to install. MANIFEST.in is what to bundle.
#   The distribute documentation says it can determine what data files to
#   include without the need of MANIFEST.in but I had no luck with that.
# - We find the bundled resource files at runtime using the pkg_resources
#   module from setuptools. Thus, setuptools is also a dependency.

# Dependencies
# - While Pygame is listed as a dependency, you should install it separately to
#   avoid issues with libpng and others.
#   See: http://www.pygame.org/install.html

setup(
    name='spyral',
    version=package_version,
    author='Platipy Project',
    author_email='platipy@platipy.org',
    install_requires=['setuptools', 'pygame>=1.8'],
    packages=['spyral'],
    description='A Python library for game development',
    long_description=open('README.rst', 'r').read(),
    keywords="pygame game engine",
    license='LGPLv2',
    url='https://github.com/platipy/spyral',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: pygame',
    ]
)
