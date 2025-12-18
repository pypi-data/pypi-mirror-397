from urllib.parse import urlunsplit

from .helpers.evaluate import (
    _has_allowed_scheme,
    _has_no_basic_auth,
    _has_no_control_character,
    _has_valid_authority_syntax,
    _has_valid_fqdn_network,
    _has_valid_fqdn_syntax,
    _has_valid_tld,
    _has_valid_tls,
)
from .helpers.sanitize import _encode_url_components, _remove_control_characters
from .utils.url import get_url_components


def evaluate_url(
        user_url: str,
        allow_http: bool = False,
        allow_localhost: bool = False,
        allow_private_ip: bool = False,
        allow_loopback_ip: bool = False,
        allow_tlsv12: bool = False) -> bool:
    """
    evaluate URL from syntax > network > transport layer
    """
    scheme, userinfo, authority, fqdn, port, _ = get_url_components(user_url)
    try:
        if all([
            _has_allowed_scheme(user_url, allow_http),
            _has_no_basic_auth(userinfo),
            _has_no_control_character(user_url),
            _has_valid_fqdn_syntax(fqdn, allow_localhost),
            _has_valid_authority_syntax(authority, port),
            _has_valid_tld(fqdn, allow_localhost),
            _has_valid_fqdn_network(fqdn, port, allow_localhost, allow_loopback_ip, allow_private_ip),
            _has_valid_tls(authority, fqdn, allow_http, allow_localhost, allow_tlsv12),
        ]):
            return True
        else:
            return False  # pragma: no cover
    except ValueError:
        return False


def sanitize_url(user_url: str) -> str:
    """
    sanitize and rebuild URL
    """
    user_url = _remove_control_characters(user_url)
    scheme, _, authority, _, _, pre_parsed_path = get_url_components(user_url)
    encoded_path, encoded_query, encoded_fragment = _encode_url_components(pre_parsed_path)

    url_components = (scheme, authority, encoded_path, encoded_query, encoded_fragment)
    return urlunsplit(url_components)
