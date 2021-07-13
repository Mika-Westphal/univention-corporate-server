#!/usr/share/ucs-test/runner pytest-3
## desc: Remove groups/group
## tags: [udm]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools


import pytest
import univention.testing.utils as utils


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_group_removal(udm):
	"""Remove groups/group"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	group = udm.create_group(wait_for=True)[0]

	udm.remove_object('groups/group', dn=group)
	utils.verify_ldap_object(group, should_exist=False)
