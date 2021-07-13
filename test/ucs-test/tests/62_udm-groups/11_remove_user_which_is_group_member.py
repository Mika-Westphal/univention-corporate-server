#!/usr/share/ucs-test/runner pytest-3
## desc: Remove a user which is member in a groups/group
## tags: [udm]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

import pytest
import univention.testing.utils as utils


@pytest.mark.tags('udm', 'apptest')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_remove_user_which_is_group_member(udm):
	"""Remove a user which is member in a groups/group"""
	## packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	user = udm.create_user()
	group = udm.create_group(users=user[0], wait_for=True)[0]
	utils.verify_ldap_object(group, {'memberUid': [user[1]], 'uniqueMember': [user[0]]})

	udm.remove_object('users/user', dn=user[0])
	utils.verify_ldap_object(group, {'memberUid': [], 'uniqueMember': []})
