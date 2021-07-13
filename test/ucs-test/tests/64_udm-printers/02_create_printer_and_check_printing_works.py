#!/usr/share/ucs-test/runner pytest-3
## desc: Create shares/printer and check if print access works
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
##   - univention-printserver


from __future__ import absolute_import
from __future__ import print_function
import ldap.dn
import univention.testing.strings as uts
import univention.testing.utils as utils
import random
import time
import subprocess
import pytest

PRINTER_PROTOCOLS = ['usb://', 'ipp://', 'socket://', 'parallel://', 'http://']


def random_fqdn(ucr):  # type: (univention.testing.ucr.UCSTestConfigRegistry) -> str
	return '%s.%s' % (uts.random_name(), ucr.get('domainname'))


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('careful')
def test_create_printer_and_check_printing_works(ucr, udm):
	"""Create shares/printer and check if print access works"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	#   - univention-printserver
	ucr.load()
	admin_dn = ucr.get('tests/domainadmin/account', 'uid=Administrator,cn=users,%s' % (ucr.get('ldap/base'),))
	admin_name = ldap.dn.str2dn(admin_dn)[0][0][1]
	password = ucr.get('tests/domainadmin/pwd', 'univention')

	spoolhost = '.'.join([ucr['hostname'], ucr['domainname']])
	acltype = random.choice(['allow all', 'allow'])

	properties = {
		'name': uts.random_name(),
		'location': uts.random_string(),
		'description': uts.random_name(),
		'spoolHost': spoolhost,
		'uri': '%s %s' % (random.choice(PRINTER_PROTOCOLS), uts.random_ip(),),
		'model': 'hp-ppd/HP/HP_Business_Inkjet_2500C_Series.ppd',
		'producer': 'cn=Generic,cn=cups,cn=univention,%s' % (ucr.get('ldap/base'),),
		'sambaName': uts.random_name(),
		'ACLtype': acltype,
		'ACLUsers': admin_dn,
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

	print('*** Modify shares/printer samba share name')
	properties['sambaName'] = uts.random_name()
	udm.modify_object('shares/printer', dn=print_share_dn, sambaName=properties['sambaName'])
	utils.verify_ldap_object(
		print_share_dn,
		{'univentionPrinterSambaName': [properties['sambaName']]},
		delay=1
	)

	delay = 15
	print('*** Wait %s seconds for listener postrun' % delay)
	time.sleep(delay)
	p = subprocess.Popen(['lpq', '-P', properties['name']], close_fds=True)
	p.wait()
	assert not p.returncode, "CUPS printer {} not created after {} seconds".format(properties['name'], delay)

	p = subprocess.Popen(['su', admin_name, '-c', 'lpr -P %s /etc/hosts' % properties['name']], close_fds=True)
	p.wait()
	assert not p.returncode, "Printing to CUPS printer {} as {} failed".format(properties['name'], admin_name)

	s4_dc_installed = utils.package_installed("univention-samba4")
	s3_file_and_print_server_installed = utils.package_installed("univention-samba")
	smb_server = s3_file_and_print_server_installed or s4_dc_installed
	if smb_server:
		delay = 1
		time.sleep(delay)
		cmd = ['smbclient', '//localhost/%s' % properties['sambaName'], '-U', '%'.join([admin_name, password]), '-c', 'print /etc/hosts']
		print('\nRunning: %s' % ' '.join(cmd))
		p = subprocess.Popen(cmd, close_fds=True)
		p.wait()
		if p.returncode:
			share_definition = '/etc/samba/printers.conf.d/%s' % properties['sambaName']
			with open(share_definition) as f:
				print('### Samba share file %s :' % share_definition)
				print(f.read())
			print('### testpam for that smb.conf section:')
			p = subprocess.Popen(['testparm', '-s', '--section-name', properties['sambaName']], close_fds=True)
			p.wait()
			assert False, 'Samba printer share {} not accessible'.format(properties['sambaName'])

	p = subprocess.Popen(['lprm', '-P', properties['name'], '-'], close_fds=True)
	p.wait()
