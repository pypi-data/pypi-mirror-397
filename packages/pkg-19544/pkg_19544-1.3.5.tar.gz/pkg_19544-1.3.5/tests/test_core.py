#!/usr/bin/env python

"""
Purpose: tests
"""
import unittest

from pkg_19544.clean_url import evaluate_url, sanitize_url


class TestCore(unittest.TestCase):
    def test_evaluate_url_example_true_scheme_yes(self):
        user_url = "https://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertTrue(evaluate_url(user_url))

    def test_evaluate_url_example_false_scheme_no(self):
        user_url = "example.com"
        self.assertFalse(evaluate_url(user_url, allow_http=True))

    def test_evaluate_url_example_true_redirect(self):
        user_url = "http://google.com"
        self.assertTrue(evaluate_url(user_url, allow_http=True, allow_redirect=True))

    def test_evaluate_url_example_false_scheme_no_enable_log(self):
        user_url = "example.com"
        self.assertFalse(evaluate_url(user_url, allow_http=True, enable_log=True))

    def test_evaluate_url_example_false_bad_scheme(self):
        user_url = "http://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_example_false_basic_auth(self):
        user_url = "https://user:pass@example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_example_false_control_char(self):
        user_url = "https://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1Nm\r\nowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_example_false_fqdn_char(self):
        user_url = "https://exa_mple.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_example_false_fqdn_label_prefix(self):
        user_url = "https://-host.example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_example_false_fqdn_label_suffix(self):
        user_url = "https://host-.example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_evaluate_url_example_false_tld(self):
        user_url = "https://example.tld8/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertFalse(evaluate_url(user_url))

    def test_sanitize_url_example_true(self):
        user_url = "https://example.com/search?q=urlencode&gs_lcrp=EgZjaHJvbzc1NmowaA&sourceid=chrome&ie=UTF-8"
        self.assertTrue(sanitize_url(user_url))
