#!/usr/share/ucs-test/runner pytest-3
## desc: create printer for every printer URI
## tags: [apptest]
## exposure: dangerous
## packages: [univention-printserver]
## bugs: [36267, 38812, 40591]

from __future__ import print_function
import re
import subprocess
import time
import univention.testing.strings as uts
import univention.testing.utils as utils
import pytest


def get_uirs():
	cmd = ['udm-test', 'settings/printeruri', 'list']
	out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	uris = re.findall(r'printeruri:\s(\w*):', out.decode('UTF-8', 'replace'))
	return uris


def printer_enabled(printer_name):
	cmd = ['lpstat', '-p']
	out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	if err:
		print('stdout from lpstat -p: %s' % out)
		print('stderr from lpstat -p: %s' % err)
	return printer_name in out.decode('UTF-8', 'replace')


@pytest.mark.tags('apptest')
@pytest.mark.exposure('dangerous')
def test_create_printer_for_every_printer_URI(ucr, udm):
	"""create printer for every printer URI"""
	# packages:
	#   - univention-printserver
	account = utils.UCSTestDomainAdminCredentials()
	position = ucr.get('ldap/hostdn').split(',', 1)[1]
	for uri in get_uirs():
		printer_name = uts.random_name()
		udm.create_object(
			modulename='shares/printer',
			name=printer_name,
			position='%s' % position,
			binddn=account.binddn,
			bindpwd=account.bindpw,
			set={
				'spoolHost': '%(hostname)s.%(domainname)s' % ucr,
				'model': 'None',
				'uri': '%s:// /tmp/%s' % (uri, printer_name)
			}
		)
		if not printer_enabled(printer_name):
			print('Wait for 30 seconds and try again')
			time.sleep(30)
			assert printer_enabled(printer_name), 'Printer (%s) is created but not enabled' % printer_name
