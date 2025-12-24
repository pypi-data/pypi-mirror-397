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
        allow_loopback_ip: bool = False,
        allow_private_ip: bool = False,
        allow_redirect: bool = True,
        allow_tlsv12: bool = False,
        skip_tls: bool = False,
        enable_log: bool = False) -> bool:
    """
    Evaluate URL from syntax to network and transport layer

    *Parameters*:

        user_url         : URL string to evaluate
        allow_http       : boolean to allow http scheme
        allow_localhost  : boolean to allow using localhost as FQDN
        allow_loopback_ip: boolean to use FQDN resolved to loopback ip address
        allow_private_ip : boolean to use FQDN resolved to private ip address
        allow_redirect   : boolean to follow redirect
        allow_tlsv12     : boolean to use TLSv1.2 in HTTPS protocol
        skip_tls         : boolean to skip TLS validation
        enable_log       : boolean to enable console logging

    *Returns*:

        Boolean
    """
    scheme, userinfo, authority, fqdn, port, pre_parsed_path = get_url_components(user_url)
    try:
        if all([
            _has_allowed_scheme(user_url, allow_http, enable_log=enable_log),
            _has_no_basic_auth(userinfo, enable_log=enable_log),
            _has_no_control_character(user_url, enable_log=enable_log),
            _has_valid_fqdn_syntax(fqdn, allow_localhost, enable_log=enable_log),
            _has_valid_authority_syntax(authority, port, enable_log=enable_log),
            _has_valid_tld(fqdn, allow_localhost, enable_log=enable_log),
            _has_valid_fqdn_network(fqdn, port, allow_localhost, allow_loopback_ip, allow_private_ip, enable_log=enable_log),
            _has_valid_tls(scheme, authority, allow_redirect, allow_tlsv12, skip_tls, enable_log=enable_log),
        ]):
            return True
        else:
            return False  # pragma: no cover
    except ValueError:
        return False


def sanitize_url(user_url: str) -> str:
    """
    Sanitize and rebuild URL

    *Parameters*:

        user_url: URL string to sanitize

    *Returns*:

        Sanitized URL string
    """
    user_url = _remove_control_characters(user_url)
    scheme, _, authority, _, _, pre_parsed_path = get_url_components(user_url)
    encoded_path, encoded_query, encoded_fragment = _encode_url_components(pre_parsed_path)

    url_components = (scheme, authority, encoded_path, encoded_query, encoded_fragment)
    return urlunsplit(url_components)
