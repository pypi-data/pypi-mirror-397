import ipaddress
import re
import socket
import ssl
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..configs.constants import (
    BLACKLIST_CIPHERS,
    BLACKLIST_CONTROL_CHARACTERS,
    HEADER_DEFAULT,
    HTTPS_TIMEOUT,
    SOCKET_TIMEOUT,
    WHITELIST_CHARS_IN_AUTHORITY,
    WHITELIST_CHARS_IN_FQDN,
    WHITELIST_HASHING_ALG,
    WHITELIST_PROTO_SCHEME,
    WHITELIST_TLS_VERSION,
)
from ..configs.tlds import TLDS
from ..utils.err import raise_on_false
from ..utils.url import get_url_components


class ValueError(ValueError):
    pass


@raise_on_false(exception_type=ValueError, message='invalid protocol scheme prefix')
def _has_allowed_scheme(
        user_url: str,
        allow_http: bool = False,
        enable_log: bool = False) -> bool:
    """
    only http(s) is supported
    """
    PROTO_SCHEME = tuple(WHITELIST_PROTO_SCHEME) + ('http://',) if allow_http else tuple(WHITELIST_PROTO_SCHEME)
    return True if user_url.lower().startswith(PROTO_SCHEME) else False


@raise_on_false(exception_type=ValueError, message='invalid URL - basic auth is not supported')
def _has_no_basic_auth(
        userinfo: str,
        enable_log: bool = False) -> bool:
    """
    userinfo is not supported
    """
    return True if not userinfo else False


@raise_on_false(exception_type=ValueError, message='invalid URL - unsupported control characters found')
def _has_no_control_character(
        user_url: str,
        enable_log: bool = False) -> bool:
    """
    Control character is not supported due to log injection risk.

    *Referencee*: https://owasp.org/www-community/attacks/Log_Injection
    """
    return False if any(char in user_url for char in BLACKLIST_CONTROL_CHARACTERS) else True


@raise_on_false(exception_type=ValueError, message='invalid FQDN - check chars usage, max length of label(63)/ fqdn(255)')
def _has_valid_fqdn_syntax(
        fqdn: str,
        allow_localhost: bool = False,
        enable_log: bool = False) -> bool:
    """
    *Notes*:

        allowed characters: https://datatracker.ietf.org/doc/html/rfc3986#section-2
    """
    if fqdn.lower() == 'localhost' and allow_localhost:
        return True
    else:
        if all([
            re.fullmatch(WHITELIST_CHARS_IN_FQDN, fqdn) is not None,
            fqdn.count('.') > 0,
            len(fqdn) <= 255,
        ]):
            list_split_fqdn = fqdn.split('.')
            for label in list_split_fqdn:
                if any([
                    not label[0].isalnum(),
                    not label[-1].isalnum(),
                    len(label) > 63
                ]):
                    return False
            return True
        else:
            return False


@raise_on_false(exception_type=ValueError, message='invalid authority - check chars usage and any port number')
def _has_valid_authority_syntax(
        authority: str,
        port: str,
        enable_log: bool = False) -> bool:
    """
    *Notes*:

        allowed characters: https://datatracker.ietf.org/doc/html/rfc3986#section-2
        allowed length    : https://datatracker.ietf.org/doc/html/rfc2181#section-11
    """
    if any([
        re.fullmatch(WHITELIST_CHARS_IN_AUTHORITY, authority) is None,
        authority.count(':') > 1,
        port.startswith('0'),
        not port.isdigit(),
        not 1 <= int(port) <= 65535 if port.isdigit() else True,
    ]):
        return False
    return True


@raise_on_false(exception_type=ValueError, message='invalid top-level domain')
def _has_valid_tld(
        fqdn: str,
        allow_localhost: bool = False,
        enable_log: bool = False) -> bool:
    """
    Check top-level domain
    """
    if fqdn.lower() == 'localhost' and allow_localhost:
        return True
    else:
        return True if fqdn.split('.')[-1:][0].upper() in TLDS else False


@raise_on_false(exception_type=ValueError, message='FQDN error at network layer')
def _has_valid_fqdn_network(
        fqdn: str,
        port: str,
        allow_localhost: bool = False,
        allow_loopback_ip: bool = False,
        allow_private_ip: bool = False,
        enable_log: bool = False) -> bool:
    """
    Check FQDN at network layer
    """
    if all([
        _is_fqdn_resolvable(fqdn, port, enable_log=enable_log),
        _is_fqdn_resolved_ip_allowed(fqdn, port, allow_localhost, allow_loopback_ip, allow_private_ip, enable_log=enable_log)
    ]):
        return True
    else:
        return False  # pragma: no cover


@raise_on_false(exception_type=ValueError, message='unable to resolve FQDN')
def _is_fqdn_resolvable(
        fqdn: str,
        port: str,
        enable_log: bool = False) -> bool:
    """
    https://docs.python.org/3/library/socket.html

    *Notes*:

        Family: AF_UNSPEC (0)
        Type  : SOCK_STREAM (1)
        Proto : IPPROTO_TCP (6)
    """
    try:
        return True if socket.getaddrinfo(fqdn, port, family=0, type=1, proto=6, flags=socket.AI_CANONNAME) else False
    except socket.gaierror:
        return False


@raise_on_false(exception_type=ValueError, message='FQDN ip address not public routable or disallowed')
def _is_fqdn_resolved_ip_allowed(
        fqdn: str,
        port: str,
        allow_localhost: bool = False,
        allow_loopback_ip: bool = False,
        allow_private_ip: bool = False,
        enable_log: bool = False) -> bool:
    """
    In an API call, FQDN that resolves to a non-Public Routable IP
    address is susceptible to Server-Side Request Forgery (SSRF) attacks.

    *Reference*: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery

    *Python ipaddress methods*:

        is_link_local: 169.254.0.0/16 (RFC 3927)
        is_link_local: fe80::/10, fe80::/64 (RFC 4291)
        is_loopback  : 127.0.0.0/8 (RFC 3330)
        is_loopback  : 0:0:0:0:0:0:0:1 or ::1 (RFC 2373)
        is_private   : 127.0.0./8 (RFC 3330)
        is_private   : 10/8, 172.16/12, 192.168/16 (RFC 1918)
        is_private   : 192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24 (RFC 5737)
        is_private   : 198.18.0.0/15 (RFC 6815)
        is_private   : fe80::/10, fe80::/64 (RFC 4291)
        is_reserved  : 240.0.0.0/4
        is_reserved  : 0:0:0:0:0:0:0:1, fe80::1, ::1 (RFC 2373)
    """
    allow_loopback_ip = True if fqdn.lower() == 'localhost' and allow_localhost else allow_loopback_ip
    allow_private_ip = True if fqdn.lower() == 'localhost' and allow_localhost else allow_private_ip
    try:
        list_addr_info = socket.getaddrinfo(fqdn, port, family=0, type=1, proto=6, flags=socket.AI_CANONNAME)
        if list_addr_info:
            for addr_info in list_addr_info:
                ip_addr = ipaddress.ip_address(addr_info[4][0])
                if any([
                    ip_addr.is_unspecified,
                    False if allow_loopback_ip else ip_addr.is_link_local,
                    False if allow_loopback_ip else ip_addr.is_loopback,
                    False if allow_loopback_ip else ip_addr.is_reserved,
                    False if allow_private_ip or ip_addr.is_loopback else ip_addr.is_private,
                ]):
                    return False
            return True
        else:
            return False
    except socket.gaierror:
        return False


@raise_on_false(exception_type=ValueError, message='invalid https certificate or connections')
def _has_valid_tls(
        scheme: str,
        authority: str,
        allow_redirect: bool = False,
        allow_tlsv12: bool = False,
        skip_tls: bool = False,
        enable_log: bool = False) -> bool:
    """
    Check TLS unless skip_tls=True
    """
    if skip_tls:
        return True
    else:
        fqdn = authority.split(':', maxsplit=1)[0] if ':' in authority else authority
        port = int(authority.split(':', maxsplit=1)[1]) if ':' in authority else 443 if scheme == 'https' else 80
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

            if allow_redirect:
                user_url = f'{scheme}://' + authority
                req = Request(user_url, headers=HEADER_DEFAULT)
                with urlopen(req, context=ssl_context, timeout=HTTPS_TIMEOUT) as response:
                    redirected_url = response.geturl()
                    _, _, _, fqdn, port, _ = get_url_components(redirected_url)

            with socket.create_connection((fqdn, int(port)), timeout=SOCKET_TIMEOUT) as sock:
                with ssl_context.wrap_socket(sock, server_hostname=fqdn) as ssock:
                    cipher_info = ssock.cipher()
                    if cipher_info:
                        cipher_name, protocol_version, _ = cipher_info
                        _has_no_blacklist_cipher(cipher_name, enable_log=enable_log)
                        _has_weak_hash_alg(cipher_name, enable_log=enable_log)
                        _has_weak_protocol(protocol_version, allow_tlsv12, enable_log=enable_log)
                        _has_invalid_expired_cert(ssock, enable_log=enable_log)
                    else:
                        return False
                return True

        except (ConnectionRefusedError, ssl.SSLError, socket.gaierror, socket.timeout, HTTPError, URLError):
            return False


@raise_on_false(exception_type=ValueError, message='TLS not using strong cipher')
def _has_no_blacklist_cipher(
        cipher_name: str,
        enable_log: bool = False) -> bool:
    return False if any(bkls_cipher.casefold() in cipher_name.casefold() for bkls_cipher in BLACKLIST_CIPHERS) else True


@raise_on_false(exception_type=ValueError, message='TLS not using strong hashing algorithm')
def _has_weak_hash_alg(
        cipher_name: str,
        enable_log: bool = False) -> bool:
    return False if not cipher_name.endswith(WHITELIST_HASHING_ALG) else True


@raise_on_false(exception_type=ValueError, message='TLS not using strong protocol')
def _has_weak_protocol(
        protocol_version: str,
        allow_tlsv12: bool = False,
        enable_log: bool = False) -> bool:
    WHITELIST_TLS_VERSION.append('TLSv1.2') if allow_tlsv12 else WHITELIST_TLS_VERSION
    return False if protocol_version not in WHITELIST_TLS_VERSION else True


@raise_on_false(exception_type=ValueError, message='invalid or expired certificate')
def _has_invalid_expired_cert(
        ssock: ssl.SSLSocket,
        enable_log: bool = False) -> bool:
    cert_dict = ssock.getpeercert()
    if isinstance(cert_dict, dict):
        cert_valid_end = cert_dict.get('notAfter')
        cert_valid_beg = cert_dict.get('notBefore')
        if isinstance(cert_valid_beg, str) and isinstance(cert_valid_end, str):
            cert_date_format = "%b %d %H:%M:%S %Y GMT"
            parsed_cert_datetime_beg = datetime.strptime(cert_valid_beg, cert_date_format)
            parsed_cert_datetime_end = datetime.strptime(cert_valid_end, cert_date_format)
            parsed_cert_datetime_beg_utc = parsed_cert_datetime_beg.astimezone(timezone.utc)
            parsed_cert_datetime_end_utc = parsed_cert_datetime_end.astimezone(timezone.utc)
            current_datetime_utc = datetime.now(timezone.utc)
            if parsed_cert_datetime_beg_utc < current_datetime_utc < parsed_cert_datetime_end_utc:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
