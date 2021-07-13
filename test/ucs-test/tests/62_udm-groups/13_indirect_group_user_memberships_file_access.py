#!/usr/share/ucs-test/runner pytest-3
## desc: Access file as user of nested group of group of files owner
## tags: [udm,apptest]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

import pytest
import atexit
import os
import subprocess
import univention.testing.strings as uts
import univention.testing.utils as utils


# for cleanup
def remove_test_file(path):
	os.remove(path)


@pytest.mark.tags('udm', 'apptest')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_indirect_group_user_memberships_file_access(udm):
	"""Access file as user of nested group of group of files owner"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	group = udm.create_group()[0]
	nested_group = udm.create_group(memberOf=group)[0]

	file_owner = udm.create_user(primaryGroup=group)
	another_user = udm.create_user(groups=nested_group)

	utils.wait_for_replication_and_postrun()
	utils.wait_for_replication_and_postrun()

	# create file as user "file_owner" and change permissions to 060 (read/write group only)
	test_file = '/var/tmp/%s' % uts.random_string()
	p = subprocess.Popen(['su', file_owner[1], '-c', 'touch %s; chmod 070 %s' % (test_file, test_file)])
	(stdout, stderr) = p.communicate()
	assert not p.returncode, 'Failed to create test file and set permissions\nstdout=%s\nstderr=%s' % (stdout, stderr) 
	atexit.register(remove_test_file, path=test_file)

	# test reading as "another_user"
	p = subprocess.Popen(['su', another_user[1], '-c', 'cat %s' % test_file])
	(stdout, stderr) = p.communicate()
	assert not p.returncode, 'Reading access to file as user of nested group of file creaters group failed\nstdout=%s\nstderr=%s' % (stdout, stderr)

	# test writing as "another_user"
	p = subprocess.Popen(['su', another_user[1], '-c', 'touch %s' % test_file])
	(stdout, stderr) = p.communicate()
	assert not p.returncode, 'Writing access to file as user of nested group of file creaters group failed\nstdout=%s\nstderr=%s' % (stdout, stderr)
