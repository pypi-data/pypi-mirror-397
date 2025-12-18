from typing import Tuple
from urllib.parse import urlparse


# http(s)://username:password@hostname.example.com:8042/path4/path44?key1=value1&key2=value2#section
# \_____/   \_______________/ \__________________/ \__/\___________/ \_____________________/ \_____/
#    |              |                   |            |        |                 |               |
# scheme        userinfo              fqdn         port      path             query         fragment
#           \_________________________________________/\___________________________________________/
#                                |                                         |
#                         authority (netloc)                        pre-parsed path


def get_url_components(user_url: str) -> Tuple[str, str, str, str, str, str]:
    default_scheme_prefix = 'http://'

    if '://' not in user_url:
        user_url = default_scheme_prefix + user_url

    scheme = urlparse(user_url).scheme
    authority = urlparse(user_url).netloc
    userinfo = authority.split('@')[0] if '@' in authority else ''

    path = f'{urlparse(user_url).path}' if urlparse(user_url).path else ''
    query = f'?{urlparse(user_url).query}' if urlparse(user_url).query else ''
    fragment = f'#{urlparse(user_url).fragment}' if urlparse(user_url).fragment else ''
    pre_parsed_path = f'{path}' + f'{query}' + f'{fragment}'
    if pre_parsed_path:
        user_url = user_url.rsplit(pre_parsed_path, maxsplit=1)[0]

    authority = user_url.replace(f'{scheme}://', '')
    authority = authority.split(f'{userinfo}@', maxsplit=1)[1] if userinfo else authority
    fqdn = authority.split(':')[0]
    port = authority.split(":")[1] if ':' in authority else '443' if scheme == 'https' else '80'

    return (scheme, userinfo, authority, fqdn, port, pre_parsed_path)
