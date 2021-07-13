#!/usr/share/ucs-test/runner pytest-3
## desc: Create shares/printer and verify LDAP object
## tags: [udm]
## roles:
##   - domaincontroller_master
##   - domaincontroller_backup
##   - domaincontroller_slave
##   - memberserver
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools


from __future__ import absolute_import
from __future__ import print_function
import univention.testing.strings as uts
import univention.testing.ucr
import univention.testing.udm as udm_test
import univention.testing.utils as utils
import random
import pytest


PRINTER_PROTOCOLS = ['usb://', 'ipp://', 'socket://', 'parallel://', 'http://']


def random_fqdn(ucr):  # type: (univention.testing.ucr.UCSTestConfigRegistry) -> str
	return '%s.%s' % (uts.random_name(), ucr.get('domainname'))


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('careful')
def test_create_printer(ucr, udm):
	"""Create shares/printer and verify LDAP object"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	ucr.load()

	properties = {
		'name': uts.random_name(),
		'location': uts.random_string(),
		'description': uts.random_name(),
		'spoolHost': random_fqdn(ucr),
		'uri': '%s %s' % (random.choice(PRINTER_PROTOCOLS), uts.random_ip(),),
		'model': 'foomatic-rip/Generic-PCL_4_Printer-gutenprint-ijs-simplified.5.2.ppd',
		'producer': 'cn=Generic,cn=cups,cn=univention,%s' % (ucr.get('ldap/base'),),
		'sambaName': uts.random_name(),
		'ACLtype': random.choice(['allow all', 'allow', 'deny']),
		'ACLUsers': 'uid=Administrator,cn=users,%s' % (ucr.get('ldap/base'),),
		'ACLGroups': 'cn=Printer Admins,cn=groups,%s' % (ucr.get('ldap/base'),),
	}

	print('*** Create shares/printer object')
	print_share_dn = udm.create_object(
		'shares/printer',
		position='cn=printers,%s' % (ucr['ldap/base'],),
		**properties)

	utils.verify_ldap_object(
		print_share_dn,
		{
			'cn': [properties['name']],
			'description': [properties['description']],
			'univentionObjectType': ['shares/printer'],
			'univentionPrinterACLGroups': [properties['ACLGroups']],
			'univentionPrinterACLUsers': [properties['ACLUsers']],
			'univentionPrinterACLtype': [properties['ACLtype']],
			'univentionPrinterLocation': [properties['location']],
			'univentionPrinterModel': [properties['model']],
			'univentionPrinterSambaName': [properties['sambaName']],
			'univentionPrinterSpoolHost': [properties['spoolHost']],
			'univentionPrinterURI': [properties['uri'].replace(' ', '')],
		},
		delay=1)

	print('*** Modify shares/printer object')
	properties['sambaName'] = uts.random_name()
	udm.modify_object('shares/printer', dn=print_share_dn, sambaName=properties['sambaName'])
	utils.verify_ldap_object(
		print_share_dn,
		{'univentionPrinterSambaName': [properties['sambaName']]},
		delay=1
	)
