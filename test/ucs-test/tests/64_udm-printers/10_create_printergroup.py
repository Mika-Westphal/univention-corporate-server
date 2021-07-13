#!/usr/share/ucs-test/runner pytest-3
## desc: Create shares/printergroup and verify LDAP object
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
import univention.testing.utils as utils
import random
import pytest

PRINTER_PROTOCOLS = ['usb://', 'ipp://', 'socket://', 'parallel://', 'http://']


def random_fqdn(ucr):  # type: (univention.testing.ucr.UCSTestConfigRegistry) -> str
	return '%s.%s' % (uts.random_name(), ucr.get('domainname'))


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('careful')
def test_create_printergroup(ucr, udm):
	"""Create shares/printergroup and verify LDAP object"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	ucr.load()

	spoolHost = random_fqdn(ucr)

	printer_properties1 = {
		'name': uts.random_name(),
		'spoolHost': spoolHost,
		'uri': '%s %s' % (random.choice(PRINTER_PROTOCOLS), uts.random_ip(),),
		'model': 'foomatic-rip/Generic-PCL_4_Printer-gutenprint-ijs-simplified.5.2.ppd',
		'producer': 'cn=Generic,cn=cups,cn=univention,%s' % (ucr.get('ldap/base'),),
	}

	print('*** Create shares/printer object')
	print_share_dn1 = udm.create_object(
		'shares/printer',
		position='cn=printers,%s' % (ucr['ldap/base'],),
		**printer_properties1)

	printer_properties2 = {
		'name': uts.random_name(),
		'spoolHost': spoolHost,
		'uri': '%s %s' % (random.choice(PRINTER_PROTOCOLS), uts.random_ip(),),
		'model': 'foomatic-rip/Generic-PCL_4_Printer-gutenprint-ijs-simplified.5.2.ppd',
		'producer': 'cn=Generic,cn=cups,cn=univention,%s' % (ucr.get('ldap/base'),),
	}

	print('*** Create shares/printer object')
	print_share_dn2 = udm.create_object(
		'shares/printer',
		position='cn=printers,%s' % (ucr['ldap/base'],),
		**printer_properties2)

	printergroup_properties = {
		'name': uts.random_name(),
		'spoolHost': spoolHost,
		'groupMember': [printer_properties1['name'], printer_properties2['name']],
		'sambaName': uts.random_name(),
	}

	print('*** Create shares/printergroup object')
	printergroup_share_dn = udm.create_object(
		'shares/printergroup',
		position='cn=printers,%s' % (ucr['ldap/base'],),
		**printergroup_properties)

	utils.verify_ldap_object(
		printergroup_share_dn,
		{
			'cn': [printergroup_properties['name']],
			'univentionObjectType': ['shares/printergroup'],
			'univentionPrinterSambaName': [printergroup_properties['sambaName']],
			'univentionPrinterSpoolHost': [printergroup_properties['spoolHost']],
			'univentionPrinterGroupMember': printergroup_properties['groupMember'],
		},
		delay=1)

	print('*** Modify shares/printergroup object')
	printergroup_properties['sambaName'] = uts.random_name()
	udm.modify_object('shares/printergroup', dn=printergroup_share_dn, sambaName=printergroup_properties['sambaName'])
	utils.verify_ldap_object(
		printergroup_share_dn,
		{'univentionPrinterSambaName': [printergroup_properties['sambaName']]},
		delay=1
	)
