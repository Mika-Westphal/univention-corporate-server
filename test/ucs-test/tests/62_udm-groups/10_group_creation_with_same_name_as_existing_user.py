#!/usr/share/ucs-test/runner pytest-3
## desc: Create groups/group with the same name as an existing user
## tags: [udm]
## roles: [domaincontroller_master]
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
def test_group_creation_with_same_name_as_existing_user(udm):
	"""Create groups/group with the same name as an existing user"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	name = uts.random_name()

	user = udm.create_user(username=name)[0]

	with pytest.raises(udm_test.UCSTestUDM_CreateUDMObjectFailed):
		group = udm.create_group(name=name)

