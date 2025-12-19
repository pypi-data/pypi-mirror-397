"""Address group MAC member exclusion check operations."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from hfortix.FortiOS.http_client import HTTPClient


class CheckAddrgrpExcludeMacMember:
    """Check if address group should exclude MAC address members."""

    def __init__(self, client: "HTTPClient"):
        """
        Initialize CheckAddrgrpExcludeMacMember endpoint.

        Args:
            client: HTTPClient instance for API communication
        """
        self._client = client

    def get(
        self,
        data_dict: Optional[Dict[str, Any]] = None,
        mkey: Optional[str] = None,
        ip_version: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Check if the IPv4 or IPv6 address group should exclude mac address type member.

        Args:
            data_dict: Optional dictionary of parameters
            mkey: Address group name (required)
            ip_version: IP version (ipv4/ipv6)
            **kwargs: Additional parameters as keyword arguments

        Returns:
            Dictionary containing check result

        Example:
            >>> fgt.api.monitor.firewall.check_addrgrp_exclude_mac_member.get(mkey='my_addrgrp')
        """
        params = data_dict.copy() if data_dict else {}
        if mkey is not None:
            params['mkey'] = mkey
        if ip_version is not None:
            params['ip_version'] = ip_version
        params.update(kwargs)
        return self._client.get("monitor", "/firewall/check-addrgrp-exclude-mac-member", params=params)
