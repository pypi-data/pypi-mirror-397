#!/usr/bin/env python

"""
Purpose: tests
"""
import socket
import unittest
from unittest.mock import patch

from apilgtm.helpers.evaluate import _has_valid_fqdn_network, _is_fqdn_resolvable, _is_fqdn_resolved_ip_allowed


class TestEvaluateUrlNetwork(unittest.TestCase):
    def test_has_valid_fqdn_network_true(self):
        fqdn = "example.com"
        port = "443"
        self.assertTrue(_has_valid_fqdn_network(fqdn, port))

    def test_is_fqdn_resolvable_true(self):
        fqdn = "example.com"
        port = "443"
        self.assertTrue(_is_fqdn_resolvable(fqdn, port))

    def test_is_fqdn_resolvable_false(self):
        fqdn = "invalid.host.example.site"
        port = "443"
        with self.assertRaises(ValueError):
            return _is_fqdn_resolvable(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_loopback_ipv4_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))
        ]
        self.assertTrue(_is_fqdn_resolved_ip_allowed(fqdn, port, allow_loopback_ip=True))

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_loopback_ipv4_not_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))
        ]
        with self.assertRaises(ValueError):
            return _is_fqdn_resolved_ip_allowed(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_loopback_ipv6_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 443))
        ]
        self.assertTrue(_is_fqdn_resolved_ip_allowed(fqdn, port, allow_loopback_ip=True))

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_loopback_ipv6_not_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('::1', 443))
        ]
        with self.assertRaises(ValueError):
            return _is_fqdn_resolved_ip_allowed(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_private_ipv4_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.30.10.30', 443))
        ]
        self.assertTrue(_is_fqdn_resolved_ip_allowed(fqdn, port, allow_private_ip=True))

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_private_ipv4_not_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.30.10.30', 443))
        ]
        with self.assertRaises(ValueError):
            return _is_fqdn_resolved_ip_allowed(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_private_ipv6_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('fc00:abcd:1234:1::1', 443))
        ]
        self.assertTrue(_is_fqdn_resolved_ip_allowed(fqdn, port, allow_private_ip=True))

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_private_ipv6_not_allowed(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('fc00:abcd:1234:1::1', 443))
        ]
        with self.assertRaises(ValueError):
            return _is_fqdn_resolved_ip_allowed(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_localhost_allowed(self, mock_getaddrinfo):
        fqdn = "localhost"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))
        ]
        self.assertTrue(_is_fqdn_resolved_ip_allowed(fqdn, port, allow_localhost=True))

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_localhost_not_allowed(self, mock_getaddrinfo):
        fqdn = "localhost"
        port = "443"
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 443))
        ]
        with self.assertRaises(ValueError):
            return _is_fqdn_resolved_ip_allowed(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_ipaddr_socket_failure(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        mock_getaddrinfo.return_value = []
        with self.assertRaises(ValueError):
            return _is_fqdn_resolved_ip_allowed(fqdn, port)

    @patch('socket.getaddrinfo')
    def test_is_fqdn_resolved_ip_allowed_socket_gaierror(self, mock_getaddrinfo):
        fqdn = "example.com"
        port = "443"
        with patch('socket.getaddrinfo') as mock_getaddrinfo:
            mock_getaddrinfo.side_effect = socket.gaierror("Unknown host")
            with self.assertRaises(ValueError):
                return _is_fqdn_resolved_ip_allowed(fqdn, port)
