# configs/constants.py

BLACKLIST_CIPHERS = ['ANON', 'EXPORT', 'NULL']
BLACKLIST_CONTROL_CHARACTERS = ['\n', '\r']

HEADER_DEFAULT = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',  # noqa: E501
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
}

HTTPS_TIMEOUT = 5
SOCKET_TIMEOUT = 2

TLD_LIST = 'src/apilgtm/configs/tlds.py'
TLD_LIVE = 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'

WHITELIST_CHARS_IN_AUTHORITY = r"^[a-zA-Z0-9\.\-\:]+$"
WHITELIST_CHARS_IN_FQDN = r"^[a-zA-Z0-9\.\-]+$"
WHITELIST_HASHING_ALG = ('SHA256', 'SHA384', 'SHA512')
WHITELIST_PROTO_SCHEME = ['https://']
WHITELIST_TLS_VERSION = ['TLSv1.3']
