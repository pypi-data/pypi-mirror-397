#!/usr/bin/env python

"""
Purpose: tests
"""
import unittest
from unittest.mock import MagicMock, patch

from apilgtm.helpers.evaluate import _has_valid_tls


class TestEvaluateUrlTls(unittest.TestCase):
    """
    when FQDN is localhost + skip_tls = True
    """
    def test_has_valid_tls_localhost_true(self):
        scheme = "http"
        authroity = "localhost"
        result = _has_valid_tls(scheme, authroity, skip_tls=True)
        assert result is True

    """
    when FQDN is localhost + no cert = False >> Raise ValueError
    """
    def test_has_valid_tls_localhost_false(self):
        scheme = "http"
        authroity = "localhost"
        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + valid cert = True
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_valid_fqdn_and_cert_true(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': 'Feb 12 12:12:12 2046 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict
        self.assertTrue(_has_valid_tls(scheme, authroity))

    """
    when FQDN is example.com + empty cipher = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_invalid_cipher_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ''

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + weak cipher = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_weak_cipher_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_NULL_SHA256', 'TLSv1.3', '256')

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + weak hashing algorithm = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_weak_hashing_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA1', 'TLSv1.3', '256')

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + weak protocol version = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_weak_protocol_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_128_GCM_SHA256', 'TLSv1.2', '128')

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + weak protocol version + allow_tlsv12 = True
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_weak_protocol_allowed_true(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': 'Feb 12 12:12:12 2046 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_128_GCM_SHA256', 'TLSv1.2', '128')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict
        self.assertTrue(_has_valid_tls(scheme, authroity, allow_tlsv12=True))

    """
    when FQDN is example.com + empty cert dict = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_cert_not_dict_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = []

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + cert notBefore is not str = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_cert_invalid_notbefore_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': {},
            'notAfter': 'Nov 12 12:12:12 2040 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + cert notAfter is not str = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_cert_invalid_notafter_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': {},
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + cert expired = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_cert_expired_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2025 GMT',
            'notAfter': 'Feb 12 12:12:12 2016 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)

    """
    when FQDN is example.com + now outside of cert window = False >> Raise ValueError
    """
    @patch('socket.create_connection')
    @patch('ssl.SSLContext.wrap_socket')
    def test_has_valid_tls_example_cert_not_ready_false(self, mock_wrap_socket, mock_create_connection):
        scheme = "https"
        authroity = "example.com"
        cert_dict = {
            'subject': (
                (('commonName', 'example.com'),),
            ),
            'issuer': (
                (('countryName', 'US'),),
                (('organizationName', "Let's Encrypt"),),
                (('commonName', 'E7'),)
            ),
            'version': 3,
            'serialNumber': '05471DE3ED23FC2DF8048F5A5621AF94242C',
            'notBefore': 'Nov 12 12:12:12 2039 GMT',
            'notAfter': 'Feb 12 12:12:12 2040 GMT',
            'subjectAltName': (('DNS', 'example.com'),),
            'caIssuers': ('http://e7.i.lencr.org/',),
            'crlDistributionPoints': ('http://e7.c.lencr.org/45.crl',)
        }

        # Configure the mock socket instance
        mock_sock = MagicMock()
        mock_create_connection.return_value.__enter__.return_value = mock_sock
        # Configure the mocked SSL socket
        mock_ssock = MagicMock()
        mock_wrap_socket.return_value.__enter__.return_value = mock_ssock
        # Configure cipher_info
        mock_ssock.cipher.return_value = ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', '256')
        # Configure get peer certificate
        mock_ssock.getpeercert.return_value = cert_dict

        with self.assertRaises(ValueError):
            return _has_valid_tls(scheme, authroity)
