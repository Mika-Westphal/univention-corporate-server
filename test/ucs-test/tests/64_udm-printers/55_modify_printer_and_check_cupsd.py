#!/usr/share/ucs-test/runner python3
## desc: Create and modify shares/printer, check if cupsd still running
## tags: [udm]
## roles:
##   - domaincontroller_master
##   - domaincontroller_slave
##   - domaincontroller_backup
##   - memberserver
## exposure: dangerous
## packages:
##   - univention-config
##   - univention-printserver
##   - univention-directory-manager-tools


import univention.testing.utils as utils
import univention.testing.strings as uts
import univention.testing.ucr
import subprocess
import time
import pytest


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('dangerous')
def test_modify_printer_and_check_cupsd(ucr, udm):
	"""Create and modify shares/printer, check if cupsd still running"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	#   - univention-printserver
	ucr.load()
	name = uts.random_name()
	printer_properties = {
		'model': 'foomatic-rip/Alps-MD-5000-md5k.ppd',
		'uri': 'file:/ tmp/%s' % name,
		'spoolHost': '%s.%s' % (ucr['hostname'], ucr['domainname']),
		'name': name,
	}
	printer = udm.create_object('shares/printer', position='cn=printers,%s' % ucr['ldap/base'], **printer_properties)
	utils.verify_ldap_object(printer, {
		'univentionPrinterModel': [printer_properties['model']],
		'univentionPrinterURI': [printer_properties['uri'].replace(' ', '')],
		'univentionPrinterSpoolHost': [printer_properties['spoolHost']]
	})
	udm.modify_object('shares/printer', dn=printer, ACLUsers=['cn=test,cn=users'], ACLtype='allow')
	time.sleep(3)
	# check if cups is still running
	subprocess.check_call(['lpstat', '-a'])
