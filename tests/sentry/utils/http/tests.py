# -*- coding: utf-8 -*-

from __future__ import absolute_import

from django.http import HttpResponse

from sentry.utils.http import is_same_domain, is_valid_origin

from sentry.testutils import TestCase


class SameDomainTestCase(TestCase):
    def test_is_same_domain(self):
        url1 = 'http://example.com/foo/bar'
        url2 = 'http://example.com/biz/baz'

        self.assertTrue(is_same_domain(url1, url2))

    def test_is_same_domain_diff_scheme(self):
        url1 = 'https://example.com/foo/bar'
        url2 = 'http://example.com/biz/baz'

        self.assertTrue(is_same_domain(url1, url2))

    def test_is_same_domain_diff_port(self):
        url1 = 'http://example.com:80/foo/bar'
        url2 = 'http://example.com:13/biz/baz'

        self.assertFalse(is_same_domain(url1, url2))


class IsValidOriginTestCase(TestCase):

    def test_project(self):
        from sentry.models import Project, ProjectOption
        project = Project.objects.get()
        ProjectOption.objects.create(project=project, key='sentry:origins', value=['http://foo.example'])

        with self.Settings(SENTRY_ALLOW_ORIGIN=None):
            self.assertFalse(is_valid_origin('http://example.com', project))

    def test_project_and_setting(self):
        from sentry.models import Project, ProjectOption
        project = Project.objects.get()
        ProjectOption.objects.create(project=project, key='sentry:origins', value=['http://foo.example'])

        with self.Settings(SENTRY_ALLOW_ORIGIN='http://example.com'):
            self.assertTrue(is_valid_origin('http://example.com', project))

    def test_setting_empty(self):
        with self.Settings(SENTRY_ALLOW_ORIGIN=None):
            self.assertFalse(is_valid_origin('http://example.com'))

    def test_setting_all(self):
        with self.Settings(SENTRY_ALLOW_ORIGIN='*'):
            self.assertTrue(is_valid_origin('http://example.com'))

    def test_setting_uri(self):
        with self.Settings(SENTRY_ALLOW_ORIGIN='http://example.com'):
            self.assertTrue(is_valid_origin('http://example.com'))
