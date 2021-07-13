#!/usr/share/ucs-test/runner pytest-3
## desc: Append nestedGroups during groups/group modification
## tags: [udm,apptest]
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
def test_group_modification_append_nestedGroups(udm):
	"""Append nestedGroups during groups/group modification"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	group = udm.create_group()[0]
	nested_groups = [udm.create_group()[0], udm.create_group()[0]]

	udm.modify_object('groups/group', dn=group, append={'nestedGroup': nested_groups})
	utils.verify_ldap_object(group, {'uniqueMember': nested_groups})
