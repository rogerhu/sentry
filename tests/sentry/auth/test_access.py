from __future__ import absolute_import

from mock import Mock

from sentry.auth import access
from sentry.models import AuthProvider
from sentry.testutils import TestCase


class FromUserTest(TestCase):
    def test_no_access(self):
        organization = self.create_organization()
        team = self.create_team(organization=organization)
        user = self.create_user()

        result = access.from_user(user, organization)
        assert not result.is_global
        assert not result.is_active
        assert result.sso_is_valid
        assert not result.scopes
        assert not result.has_team(team)

    def test_global_org_member_access(self):
        user = self.create_user()
        organization = self.create_organization(owner=user)
        member = organization.member_set.get(user=user)
        team = self.create_team(organization=organization)

        result = access.from_user(user, organization)
        assert result.is_global
        assert result.is_active
        assert result.sso_is_valid
        assert result.scopes == member.scopes
        assert result.has_team(team)

    def test_team_restricted_org_member_access(self):
        user = self.create_user()
        organization = self.create_organization()
        team = self.create_team(organization=organization)
        member = organization.member_set.create(
            organization=organization,
            user=user,
            has_global_access=False,
        )
        member.teams.add(team)

        result = access.from_user(user, organization)
        assert not result.is_global
        assert result.is_active
        assert result.sso_is_valid
        assert result.scopes == member.scopes
        assert result.has_team(team)

    def test_unlinked_sso(self):
        user = self.create_user()
        organization = self.create_organization(owner=user)
        member = organization.member_set.get(user=user)
        team = self.create_team(organization=organization)
        AuthProvider.objects.create(
            organization=organization,
            provider='dummy',
        )

        result = access.from_user(user, organization)
        assert not result.sso_is_valid

    def test_sso_without_link_requirement(self):
        user = self.create_user()
        organization = self.create_organization(owner=user)
        member = organization.member_set.get(user=user)
        team = self.create_team(organization=organization)
        AuthProvider.objects.create(
            organization=organization,
            provider='dummy',
            flags=AuthProvider.flags.allow_unlinked,
        )

        result = access.from_user(user, organization)
        assert result.sso_is_valid

    def test_anonymous_user(self):
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()
        organization = self.create_organization(owner=user)
        result = access.from_user(user, organization)

        assert result.is_active


class DefaultAccessTest(TestCase):
    def test_no_access(self):
        result = access.DEFAULT
        assert not result.is_global
        assert not result.is_active
        assert result.sso_is_valid
        assert not result.scopes
        assert not result.has_team(Mock())
