#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# Univention Management Console module:
#   Support health UMC module
#
# Copyright 2014 Univention GmbH
#
# http://www.univention.de/
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
# /usr/share/common-licenses/AGPL-3; if not, seGe
# <http://www.gnu.org/licenses/>.

from os import listdir

from univention.lib.i18n import Translation
from univention.management.console.modules import Base
from univention.management.console.log import MODULE

from plugins import getPlugin, Plugin

_ = Translation('univention-management-console-module-diagnostic').translate


class Instance(Base):

	def run(self, request):
		'''Run requested plugins.

		request.options is an array containing the file names of the requested
		plugins.
		'''

		for plugin_filename in request.options:
			plugin = getPlugin(plugin_filename)
			if plugin.validHeader:
				plugin.execute()
		self.finished(request.id, [])

	@simple_response
	def query(self, searchPattern):
		result = []
		for plugin_filename in listdir(Plugin.ROOT_DIRECTORY):
			plugin = getPlugin(plugin_filename)

			if not plugin.validHeader or not searchPattern.lower() in plugin.header['title'].lower():
				continue

			result.append(dict(
				plugin_filename=plugin.fileName,
				title=plugin.header['title'],
				description=plugin.header['description'],
				**plugin.status
			))
		return result

	def get(self, request):
		'''
		Get all information about a plugin and its last execution result.

		Due to UMC definitions, request.options is an array containing only the
		file name of the requested plugin instead of a simple string.
		'''

		plugin = getPlugin(request.options[0])
		self.finished(request.id, [dict(
			plugin_filename=plugin.fileName,
			title=plugin.header['title'],
			description=plugin.header['description'],
			**plugin.lastResult
		)])
