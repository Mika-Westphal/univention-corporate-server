#!/usr/share/ucs-test/runner pytest-3
## desc: Check different case in LDAP DN of group modifications
## tags: [udm]
## roles: [domaincontroller_master]
## exposure: careful
## packages:
##   - univention-config
##   - univention-directory-manager-tools

from __future__ import print_function
import ldap
import pytest

import univention.testing.utils as utils
import univention.testing.strings as uts


@pytest.mark.tags('udm')
@pytest.mark.roles('domaincontroller_master')
@pytest.mark.exposure('careful')
def test_group_different_case(udm):
	"""Check different case in LDAP DN of group modifications"""
	# packages:
	#   - univention-config
	#   - univention-directory-manager-tools
	user = udm.create_user()[0]
	nested_group = udm.create_group()[0]
	computer = udm.create_object('computers/windows', name=uts.random_string())

	group = udm.create_group(hosts=computer, users=user, nestedGroup=nested_group, wait_for=True)[0]
	utils.verify_ldap_object(group, {'uniqueMember': [user, nested_group, computer]})

	for members in changed_cases(dict(hosts=computer, users=user, nestedGroup=nested_group)):
		print('Modifying group with changed members: %r' % (members,))
		udm.modify_object('groups/group', dn=group, remove=dict(hosts=[computer], users=[user], nestedGroup=[nested_group]), wait_for=True)
		# FIXME: Bug #43286: udm.modify_object('groups/group', dn=group, remove=members)
		utils.verify_ldap_object(group, {'uniqueMember': []})

		udm.modify_object('groups/group', dn=group, append=members, wait_for=True)
		utils.verify_ldap_object(group, {'uniqueMember': [user, nested_group, computer]})


def changed_cases(members):
	variants = []
	for transform in (str.lower, str.upper, mixed_case):
		result = {}
		for key, dn in members.items():
			dn = ldap.dn.str2dn(dn)
			rdn = dn.pop(0)
			rdn = [tuple([transform(str(rdn[0][0]))] + list(rdn[0][1:]))]
			dn.insert(0, rdn)
			result[key] = [ldap.dn.dn2str(dn)]
		variants.append(result)
	return variants


def mixed_case(attr):
	return attr[0].lower() + attr[1:].upper()
