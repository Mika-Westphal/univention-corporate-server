#!/usr/share/ucs-test/runner pytest-3
## desc: Add nestedGroup with single letter name to groups/group during creation
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
def test_group_creation_set_single_letter_name_nestedGroup(udm):
	"""Add nestedGroup with single letter name to groups/group during creation"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	nestedGroup = udm.create_group(name=uts.random_groupname(1))[0]
	group = udm.create_group(nestedGroup=nestedGroup)[0]

	utils.verify_ldap_object(group, {'uniqueMember': [nestedGroup]})
