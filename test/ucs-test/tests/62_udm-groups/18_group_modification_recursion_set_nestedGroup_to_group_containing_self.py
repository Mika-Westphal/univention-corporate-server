#!/usr/share/ucs-test/runner pytest-3
## desc: groups/group recursion due setting group as nestedGroup which already contains self as nested group during modification
## tags: [udm]
## roles: [domaincontroller_master]
## bugs: [13008]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

import pytest
import univention.testing.udm as udm_test


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def self_group_modification_recursion_set_nestedGroup_to_group_containing_self(udm):
	"""groups/group recursion due setting group as nestedGroup which already contains self as nested group during modification"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	group = udm.create_group()[0]
	group2 = udm.create_group(nestedGroup=group)[0]

	with pytest.raises(udm_test.UCSTestUDM_ModifyUDMObjectFailed):
		udm.modify_object('groups/group', dn=group, nestedGroup=group2)
