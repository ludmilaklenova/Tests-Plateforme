# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
#  Copyright (c) 2018 Synchrotron Soleil
#
#  Distributed under the terms of the GNU LGPL.
#
#  The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
"""Release data for the tests platform project."""

name = 'tests platform'

# Tests platform version information.  An empty _version_extra corresponds to a full
# release.  'dev' as a _version_extra string means this is a development
# version
_version_major = 0
_version_minor = 0
_version_micro = 1  # ''  # use '' for first of series, number for 1 and above

_version_extra = ''  #  full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor, _version_micro]

if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

version = __version__  # backwards compatibility name

description = "Tests platform tool"

license = 'add a license'

authors = {
    'Ludmila': ('Ludmila Klenov',
              'ludmila.klenov@synchrotron-soleil.fr'),
    'Sandra': ('Sandra Pierre-Joseph Zephir',
               'pierrejoseph@synchrotron-soleil.fr')
}

author = 'Ludmila Klenov'
author_email = 'ludmila.klenov@synchrotron-soleil.fr'
maintainer = 'Sandra Pierre-Joseph Zephir'
maintainer_email = 'pierrejoseph@synchrotron-soleil.fr'

url = 'http://www.synchrotron-soleil.fr'
download_url = ''

platforms = ['Linux' ]

keywords = ['Tests', 'packages', 'ICA']

classifiers = [
    'Development Status :: 1 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License (LGPL)',
    'Environment :: Console',
    'Operating System :: POSIX',
    'Framework :: robot framework',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Topic :: System :: SCADA',
    'Topic :: System :: Shells'
]
