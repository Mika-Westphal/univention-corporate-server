#!/usr/share/ucs-test/runner pytest-3
## desc: Rename group/groups which contains a nested groups/group
## tags: [udm,apptest]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

import pytest
import univention.testing.strings as uts
import univention.testing.utils as utils


@pytest.mark.tags('udm', 'apptest')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_rename_a_group_which_contains_a_nestedGroup(udm):
	"""Rename group/groups which contains a nested groups/group"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	nested_group = udm.create_group()[0]
	group = udm.create_group(nestedGroup=nested_group)[0]

	new_group_name = uts.random_groupname()
	udm.modify_object('groups/group', dn=group, name=new_group_name)
	group = 'cn=%s,%s' % (new_group_name, ','.join(group.split(',')[1:]))
	utils.verify_ldap_object(group, {'uniqueMember': [nested_group]})
