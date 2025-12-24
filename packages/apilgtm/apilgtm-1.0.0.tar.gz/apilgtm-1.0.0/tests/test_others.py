#!/usr/bin/env python

"""
Purpose: tests
"""
import unittest

from apilgtm.helpers.evaluate import (
    _has_allowed_scheme,
    _has_no_basic_auth,
    _has_no_control_character,
    _has_valid_authority_syntax,
    _has_valid_fqdn_syntax,
    _has_valid_tld,
)
from apilgtm.helpers.sanitize import _encode_url_components, _remove_control_characters


class TestEvaluateUrl(unittest.TestCase):
    """
    test allowed scheme
    """
    def test_has_allowed_scheme_true(self):
        user_url = "https://example.com/path1/path2?key=value#section1.1"
        self.assertTrue(_has_allowed_scheme(user_url))

    def test_has_allowed_scheme_false(self):
        user_url = "http://example.com/path1/path2?key=value#section1.1"
        with self.assertRaises(ValueError):
            return _has_allowed_scheme(user_url)

    """
    test userinfo
    """
    def test_has_no_basic_auth_true(self):
        userinfo = ""
        self.assertTrue(_has_no_basic_auth(userinfo))

    def test_has_no_basic_auth_false(self):
        userinfo = "user:pass"
        with self.assertRaises(ValueError):
            return _has_no_basic_auth(userinfo)

    """
    test control character
    """
    def test_has_no_control_character_true(self):
        user_url = "https://example.com/path1/path2?key=value#section1.1"
        self.assertTrue(_has_no_control_character(user_url))

    def test_has_no_control_character_false(self):
        user_url = "http://example.com/pa\nth1/path2?key=va\rlue#section1.1"
        with self.assertRaises(ValueError):
            return _has_no_control_character(user_url)

    """
    test fqdn syntax - localhost
    """
    def test_has_valid_fqdn_syntax_true_localhost(self):
        fqdn = "localhost"
        self.assertTrue(_has_valid_fqdn_syntax(fqdn, allow_localhost=True))

    """
    test fqdn syntax - not localhost
    """
    def test_has_valid_fqdn_syntax_true(self):
        fqdn = "example.com"
        self.assertTrue(_has_valid_fqdn_syntax(fqdn))

    def test_has_valid_fqdn_syntax_false_chars_not_match(self):
        fqdn = "examp:lecom"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_false_no_dot(self):
        fqdn = "examplecom"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_false_length_over_255(self):
        fqdn = "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "1234567890.1234567890.1234567890.1234567890.1234567890." \
               "example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_label_true(self):
        fqdn = "12345678901234567890123456789012345678901234567890.example.com"
        self.assertTrue(_has_valid_fqdn_syntax(fqdn))

    def test_has_valid_fqdn_syntax_label_false_hyphen_prefix(self):
        fqdn = "-host.example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_label_false_hyphen_suffix(self):
        fqdn = "host-.example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    def test_has_valid_fqdn_syntax_label_false_length(self):
        fqdn = "12345678901234567890123456789012345678901234567890" \
               "123456789012345678901234.example.com"
        with self.assertRaises(ValueError):
            return _has_valid_fqdn_syntax(fqdn)

    """
    test authority syntax
    """
    def test_has_valid_authority_syntax_true(self):
        authority = "example.com:9090"
        port = "9090"
        self.assertTrue(_has_valid_authority_syntax(authority, port))

    def test_has_valid_authority_syntax_false_count_colon(self):
        authority = "example:com:9090"
        port = "9090"
        with self.assertRaises(ValueError):
            return _has_valid_authority_syntax(authority, port)

    def test_has_valid_authority_syntax_false_port0(self):
        authority = "example:com:9090"
        port = "0100"
        with self.assertRaises(ValueError):
            return _has_valid_authority_syntax(authority, port)

    def test_has_valid_authority_syntax_false_port_not_digit(self):
        authority = "example:com:9090"
        port = "abc"
        with self.assertRaises(ValueError):
            return _has_valid_authority_syntax(authority, port)

    def test_has_valid_authority_syntax_false_port_over_65535(self):
        authority = "example:com:9090"
        port = "99999"
        with self.assertRaises(ValueError):
            return _has_valid_authority_syntax(authority, port)

    """
    test tld
    """
    def test_has_valid_tld_true(self):
        fqdn = "host.example.com"
        self.assertTrue(_has_valid_tld(fqdn))

    def test_has_valid_tld_true_localhost(self):
        fqdn = "localhost"
        self.assertTrue(_has_valid_tld(fqdn, allow_localhost=True))

    def test_has_valid_tld_false_invalid_tld(self):
        fqdn = "host.example.x0m"
        with self.assertRaises(ValueError):
            return _has_valid_tld(fqdn)


class TestSanitizeUrl(unittest.TestCase):
    def test_remove_control_characters_true_control_chars_no(self):
        user_url = "https://example.com/search+test?key1=value1#section-3.11"

        updated_url = _remove_control_characters(user_url)
        assert updated_url is not None

    def test_remove_control_characters_true_control_chars_yes(self):
        user_url = "https://example.com/search+te\rst?key1=val\r\nue1#section-3.11 "
        user_url_length = len(user_url)

        updated_url = _remove_control_characters(user_url)
        updated_url_length = len(updated_url)

        diff = user_url_length - updated_url_length

        assert updated_url is not None
        assert diff == 4
        assert updated_url == "https://example.com/search+test?key1=value1#section-3.11"

    def test_encode_url_components_true(self):
        pre_parsed_path = "/search+test?key1=value1&key2='value2'#section-3.11"

        updated_url = _encode_url_components(pre_parsed_path)
        assert "/" in updated_url[0]
        assert "+" in updated_url[0]
        assert "&" in updated_url[1]
        assert "=" in updated_url[1]
        assert "%27" in updated_url[1]
        assert "?" not in updated_url[1]
        assert "#" not in updated_url[2]
