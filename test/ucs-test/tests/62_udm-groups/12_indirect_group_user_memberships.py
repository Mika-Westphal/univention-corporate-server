#!/usr/share/ucs-test/runner pytest-3
## desc: Test indirect group memberships of users
## tags: [udm,apptest]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

import pytest
import grp
import univention.testing.utils as utils

@pytest.mark.tags('udm', 'apptest')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_indirect_group_user_memberships(udm):
	"""Test indirect group memberships of users"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	group = udm.create_group()
	nested_group = udm.create_group(memberOf=group[0])
	user = udm.create_user(groups=nested_group[0])

	for group in grp.getgrall():
		if group.gr_name == group[1]:
			assert user[1] in group.gr_mem, 'User %s is no indirect member of group %s' % (user[1], group[1])
			break
