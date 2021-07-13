#!/usr/share/ucs-test/runner pytest-3
# -*- coding: utf-8 -*-
## desc: Create groups/group with umlaut in name
## tags: [udm,apptest,SKIP]
## bugs: [35521]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

# This test case is strange: Initially (2013) it should check that
# the "gid" UDM syntax doesn't allow non-ASCII chracters.
# But then, in 2014 Bug #35521 made a change to allow non-ASCII characters,
# but that adjustment only had an effect for group names passed as unicode,
# which probably is the case in case a UDM group is created via AD-Connector
# So we have an inconsistent behavior here with PYthon2, Umlauts in group
# names are allowed when passed as unicode, but, as the continued success of
# this test case here shows, they apparently are not allowed, when passed
# via udm-cli (probably as UTF-8 bytes).
#
# I set this test case to SKIP for now, because it didn't work any longer
# for Python3 UDM, at the time of writing, as the value passed to the
# "gid" UDM syntax is unicode now even when used from udm-cli. I don't think
# we want to explicitly lower the bar again to the state of 2013.
# Also I think it is more consistend to always allow Umlaut characters in
# group names, not only when used from python, as done on the AD-Connector.
# This should not be a problem since they are stored in LDAP as UTF-8.


import pytest
import univention.testing.strings as uts
import univention.testing.udm as udm_test


@pytest.mark.tags('udm', 'apptest')
@pytest.mark.xfail(reason='Bug #35521')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_group_creation_with_umlaut_in_name(udm):
	"""Create groups/group with umlaut in name"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	with pytest.raises(udm_test.UCSTestUDM_CreateUDMObjectFailed):
		group = udm.create_group(name='%säÄöÖüÜ%s' % (uts.random_groupname(4), uts.random_groupname(4)))[0]
		# group = udm.create_group(name='Contrôleurs de domaine d’entreprise')[0]
