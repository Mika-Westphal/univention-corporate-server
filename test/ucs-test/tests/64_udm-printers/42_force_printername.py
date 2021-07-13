#!/usr/share/ucs-test/runner pytest-3
## desc: Check state of "force printername" during UDM printer modify
## tags: [udm]
## roles:
##   - domaincontroller_master
##   - domaincontroller_slave
##   - domaincontroller_backup
##   - memberserver
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools
##   - univention-printserver
##   - samba-common-bin


from __future__ import print_function
import univention.testing.utils as utils
import univention.testing.strings as uts
import univention.config_registry
import subprocess
import pytest
import os


def get_testparm_var(smbconf, sectionname, varname):
	if not os.path.exists("/usr/bin/testparm"):
		return False

	cmd = [
		"/usr/bin/testparm", "-s", "-l",
		"--section-name=%s" % sectionname,
		"--parameter-name=%s" % varname,
		smbconf]
	p1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
	(out, err) = p1.communicate()
	return out.strip().decode('UTF-8', 'replace')


@pytest.mark.skip(reason="It's no test")
def testparm_is_true(smbconf, sectionname, varname):
	testpram_output = get_testparm_var(smbconf, sectionname, varname)
	return testpram_output.lower() in ('yes', 'true', '1', 'on')


def rename_share_and_check(udm, printer, expected_value):
	printer_samba_name = uts.random_name()
	udm.modify_object('shares/printer', dn=printer, sambaName=printer_samba_name)
	utils.verify_ldap_object(printer, {'univentionPrinterSambaName': [printer_samba_name]})
	utils.wait_for_replication()

	filename = '/etc/samba/printers.conf.d/%s' % printer_samba_name
	samba_force_printername = testparm_is_true(filename, printer_samba_name, 'force printername')
	assert samba_force_printername == expected_value, "samba option \"force printername\" changed after UDM share modification"
	print("Ok, samba option \"force printername\" still set to %s" % (expected_value,))


@pytest.mark.skip(reason="It's no test")
def test_run(udm, ucr, test_ucr_value):
	ucr_var = "samba/force_printername"

	ucr.load()
	previous_value = ucr.get(ucr_var)

	if test_ucr_value is None:
		univention.config_registry.handler_unset([ucr_var])

	else:
		keyval = "%s=%s" % (ucr_var, test_ucr_value)
		univention.config_registry.handler_set([keyval])

	if test_ucr_value != previous_value:
		p1 = subprocess.Popen(["systemctl", "restart", "univention-directory-listener"], close_fds=True)
		p1.wait()

	ucr.load()
	expected_value = ucr.is_true(ucr_var, True)  # This is the behavior of cups-printers.py

	printer_name = uts.random_name()

	printer_properties = {
		'model': 'foomatic-ppds/Apple/Apple-12_640ps-Postscript.ppd.gz',
		'uri': 'parallel /dev/lp0',
		'spoolHost': '%s.%s' % (ucr['hostname'], ucr['domainname']),
		'name': printer_name
	}

	printer = udm.create_object('shares/printer', position='cn=printers,%s' % ucr['ldap/base'], **printer_properties)
	utils.verify_ldap_object(printer, {
		'univentionPrinterModel': [printer_properties['model']],
		'univentionPrinterURI': [printer_properties['uri'].replace(' ', '')],
		'univentionPrinterSpoolHost': [printer_properties['spoolHost']]
	})
	utils.wait_for_replication()

	old_filename = '/etc/samba/printers.conf.d/%s' % printer_name
	samba_force_printername = testparm_is_true(old_filename, printer_name, 'force printername')
	assert samba_force_printername == expected_value, "samba option \"force printername\" not set to %s" % (expected_value,)
	print("Ok, samba option \"force printername\" set to %s" % (expected_value,))

	# Check behavior during UDM modification
	rename_share_and_check(udm, printer, expected_value)

	# And check again after inverting the UCR setting:
	if not expected_value:
		# This simulates the update case
		keyval = "%s=%s" % (ucr_var, "yes")
		univention.config_registry.handler_set([keyval])
	else:
		keyval = "%s=%s" % (ucr_var, "no")
		univention.config_registry.handler_set([keyval])

	p1 = subprocess.Popen(["systemctl", "restart", "univention-directory-listener"], close_fds=True)
	p1.wait()

	rename_share_and_check(udm, printer, expected_value)


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('careful')
def test_force_printername(ucr, udm):
	"""Check state of "force printername" during UDM printer modify"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	#   - univention-printserver
	#   - samba-common-bin
	test_run(udm, ucr, None)
	test_run(udm, ucr, "false")

	# restart listener with original UCR values:
	p1 = subprocess.Popen(["systemctl", "restart", "univention-directory-listener"], close_fds=True)
	p1.wait()
