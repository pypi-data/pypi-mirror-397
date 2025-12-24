from urllib import request
from urllib.error import HTTPError, URLError

from apilgtm.configs.constants import TLD_LIST, TLD_LIVE


def get_tlds() -> bool:
    """
    Create a list that contains all top-level domains
    """
    try:
        with request.urlopen(TLD_LIVE) as response:
            html_bytes = response.read()
            html_string = html_bytes.decode('utf-8')
            list_tld = html_string.splitlines()[1:]

            with open(TLD_LIST, 'w') as f:
                tld_key = "TLDS"
                tld_val = str(list_tld).replace(" ", "\r\n    ").replace("['", "[\r\n    '").replace("]", "]\r\n")
                f.write(f'{tld_key} = {tld_val}')
            return True

    except (HTTPError, URLError, TimeoutError, ValueError):
        return False


if __name__ == "__main__":
    get_tlds()
