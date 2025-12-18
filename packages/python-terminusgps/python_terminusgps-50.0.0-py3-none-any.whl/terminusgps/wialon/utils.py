import secrets
import string

from terminusgps.wialon.session import WialonSession


def get_id_from_iccid(
    iccid: str,
    session: WialonSession,
    *,
    use_cache: bool = True,
    afield_key: str = "iccid",
) -> int | None:
    """
    Returns a Wialon unit ID from a telecom iccid.

    :param iccid: A telecom iccid number.
    :type iccid: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param use_cache: Whether to use a cached Wialon API response or force a Wialon API call. Default is :py:obj:`True`.
    :type use_cache: bool
    :param afield_key: Admin field key to search against. Default is ``"iccid"``.
    :type afield_key: str
    :raises ValueError: If multiple units were found with the provided iccid.
    :raises ValueError: If zero units were found with the provided iccid.
    :returns: A Wialon unit ID, if found.
    :rtype: int | None

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "rel_adminfield_name,rel_adminfield_value",
                "propValueMask": f"{afield_key},{iccid}",
                "sortType": "sys_name",
                "propType": "admin_fields,admin_fields",
            },
            "force": int(not use_cache),
            "flags": 1,
            "from": 0,
            "to": 0,
        }
    )
    if int(response["totalItemsCount"]) > 1:
        raise ValueError(f"Multiple units found for iccid #{iccid}.")
    elif int(response["totalItemsCount"]) == 0:
        raise ValueError(f"No units found for iccid #{iccid}.")
    return int(response["items"][0]["id"])


def get_id_from_imei(
    imei: str, session: WialonSession, *, use_cache: bool = True
) -> int | None:
    """
    Returns a Wialon unit ID from an IMEI (sys_unique_id) number.

    :param imei: An IMEI number.
    :type imei: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param use_cache: Whether to use a cached Wialon API response or force a Wialon API call. Default is :py:obj:`True`.
    :type use_cache: bool
    :raises ValueError: If multiple units were found with the provided IMEI number.
    :raises ValueError: If zero units were found with the provided IMEI number.
    :returns: A Wialon unit ID, if found.
    :rtype: int | None

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": imei,
                "sortType": "sys_name",
                "propType": "property",
            },
            "force": int(not use_cache),
            "flags": 1,
            "from": 0,
            "to": 0,
        }
    )
    if int(response["totalItemsCount"]) > 1:
        raise ValueError(f"Multiple units found for IMEI #{imei}.")
    elif int(response["totalItemsCount"]) == 0:
        raise ValueError(f"No units found for IMEI #{imei}.")
    return int(response["items"][0]["id"])


def get_ids_from_carrier(
    carrier: str,
    session: WialonSession,
    *,
    use_cache: bool = True,
    afield_key: str = "carrier",
) -> list[int]:
    """
    Returns a list of Wialon unit IDs by telecom carrier name.

    The list may be empty if no units were found.

    :param carrier: A telecom carrier name.
    :type carrier: str
    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param use_cache: Whether to use a cached Wialon API response or force a Wialon API call. Default is :py:obj:`True`.
    :type use_cache: bool
    :param afield_key: Admin field key to search against. Default is ``"carrier"``.
    :type afield_key: str
    :returns: A list of Wialon unit IDs, if any were found.
    :rtype: list[int]

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "rel_adminfield_name,rel_adminfield_value",
                "propValueMask": f"{afield_key},{carrier}",
                "sortType": "sys_name",
                "propType": "admin_fields,admin_fields",
            },
            "force": int(not use_cache),
            "flags": 1,
            "from": 0,
            "to": 0,
        }
    )
    if int(response["totalItemsCount"]) == 0:
        return []
    return [int(unit["id"]) for unit in response["items"]]


def generate_wialon_password(length: int = 32) -> str:
    """
    Generates a Wialon compliant password between ``8`` and ``64`` characters.

    The generated password will contain:

        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one special symbol.
        - At least three digits.

    :param length: Length of the generated password. Default is ``32``.
    :type length: int
    :raises ValueError: If ``length`` was less than ``8`` or greater than ``64``.
    :returns: A Wialon compliant password.
    :rtype: str

    """
    if length > 64:
        raise ValueError(
            f"Password cannot be greater than 64 characters in length, got {length}."
        )
    elif length < 8:
        raise ValueError(
            f"Password cannot be less than 8 characters in length, got {length}."
        )

    s0 = list(string.ascii_uppercase)
    s1 = list(string.ascii_lowercase)
    s2 = list(string.digits)
    s3 = list("!@#$%^*()[]-_+")

    while True:
        password = "".join(
            [secrets.choice(s0 + s1 + s2 + s3) for _ in range(length)]
        )
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
            and any(c in s3 for c in password)
        ):
            break
    return password
