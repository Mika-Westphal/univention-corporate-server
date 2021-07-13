#!/usr/share/ucs-test/runner pytest-3
## desc: Rename a nested groups/group
## tags: [udm]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

import pytest
import univention.testing.strings as uts
import univention.testing.utils as utils
from univention.testing.ucs_samba import wait_for_s4connector


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_rename_a_neasted_group(udm):
	"""Rename a nested groups/group"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	nested_group = udm.create_group()[0]
	group = udm.create_group(nestedGroup=nested_group)[0]
	wait_for_s4connector()
	new_nested_group_name = uts.random_groupname()
	udm.modify_object('groups/group', dn=nested_group, name=new_nested_group_name)
	wait_for_s4connector()
	nested_group = 'cn=%s,%s' % (new_nested_group_name, ','.join(nested_group.split(',')[1:]))
	utils.verify_ldap_object(group, {'uniqueMember': [nested_group]})
