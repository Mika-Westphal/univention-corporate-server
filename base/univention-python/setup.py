#!/usr/bin/python3
#
# Copyright 2019-2020 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.

import os.path
from distutils.core import setup
from univention.python_packaging.debian_package import DebianPackage

#
# If you get "fatal error: crack.h: No such file or directory", the "dev"
# package of cracklib is not installed. Install it:
# apt install libcrack2-dev
#

dp = DebianPackage(os.path.dirname(__file__))

setup(
	packages=['univention'],
	package_dir={'': 'modules'},
	license='GNU Affero General Public License v3',
	**dp.as_setuptools_setup_kwargs()
)
