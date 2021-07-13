#!/usr/share/ucs-test/runner pytest-3
## desc: groups/group recursion due setting self as nestedGroup during creation
## tags: [udm]
## roles: [domaincontroller_master]
## bugs: [13008]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools


import pytest
import univention.testing.strings as uts
import univention.testing.udm as udm_test


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_group_creation_recursion_set_nestedGroup_to_self(udm):
	"""groups/group recursion due setting self as nestedGroup during creation"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	group_name = uts.random_groupname()
	with pytest.raises(udm_test.UCSTestUDM_CreateUDMObjectFailed):
		udm.create_group(name=group_name, nestedGroup='cn=%s,cn=groups,%s' % (group_name, udm.LDAP_BASE))
