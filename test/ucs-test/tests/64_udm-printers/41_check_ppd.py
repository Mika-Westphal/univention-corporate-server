#!/usr/share/ucs-test/runner pytest-3
## desc: Check PPD files
## tags: [udm]
## bugs: [43417]
## roles:
##   - domaincontroller_master
##   - domaincontroller_slave
##   - domaincontroller_backup
##   - memberserver
## exposure: safe
## packages:
##   - univention-config
##   - univention-directory-manager-tools
##   - univention-printserver

from __future__ import print_function

import os
import sys
import shlex
import pytest
import subprocess
import univention.testing.utils as utils


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master', 'domaincontroller_backup', 'domaincontroller_slave', 'memberserver')
@pytest.mark.exposure('safe')
def test_check_ppd():
	"""Create shares/printer and check if print access works"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	#   - univention-printserver
	ldap_printer = []
	printer_files = []
	print('searching for printer models')
	for dn, attr in utils.get_ldap_connection().search(filter='(objectClass=univentionPrinterModels)', attr=['printerModel']):
		for printerModel in attr.get('printerModel', ()):
			printerModel = printerModel.decode('UTF-8')
			model, desc = shlex.split(printerModel)
			desc = printerModel.split('"')[3]
			if desc.startswith('deprecated (only available'):
				continue
			if model.endswith('.ppd') or model.endswith('.ppd.gz'):
				model = model.split('/')[-1]
				ldap_printer.append(model)

	for root, dirs, files in os.walk('/usr/share/ppd/'):
		for file_ in files:
			if file_.endswith('.ppd') or file_.endswith('ppd.gz'):
				printer_files.append(file_)

	for line in subprocess.check_output(['/usr/lib/cups/driver/foomatic-db-compressed-ppds', 'list']).decode('UTF-8', 'replace').splitlines():
		file_ = shlex.split(line)[0]
		printer_files.append(file_.split('/')[-1])

	# check if we found something
	assert ldap_printer
	assert printer_files

	# check diff
	missing_files = set(ldap_printer) - set(printer_files)
	missing_printers = set(printer_files) - set(ldap_printer)
	message = ''
	if missing_files:
		# ignore missing cups-pdf ppd (univention-cups-pdf is not installed)
		if missing_files - {'CUPS-PDF.ppd', 'CUPS-PDF_opt.ppd', 'CUPS-PDF_noopt.ppd'}:
			message += 'No PPD file found for LDAP printers:\n' + '\n\t'.join(missing_files)
	if missing_printers:
		message += '\n\n' + 'No LDAP printer found for PPD files:\n' + '\n\t'.join(missing_printers)
	if message:
		print(message, file=sys.stderr)
		sys.exit(1)
