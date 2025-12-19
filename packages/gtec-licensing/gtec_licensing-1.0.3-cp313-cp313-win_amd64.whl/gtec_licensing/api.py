from enum import IntEnum
from typing import List, Optional, Tuple

from .lib.gtec_licensing_lib import GtecLicensingLib


class ErrorCode(IntEnum):
    SUCCESS = 0
    INVALID_FOLDER_STRUCTURE = 1
    INVALID_LICENSE_FILE = 2
    SYSTEM_INFO_FAILED = 3
    ENCRYPTION_FAILED = 4
    WEB_REQUEST_FAILED = 5
    NO_ACTIVATIONS_LEFT = 6
    ALREADY_ACTIVATED = 7
    OFFLINE_USAGE_TIMESPAN_EXPIRED = 8
    INVALID_LICENSE = 9
    LICENSE_NOT_FOUND = 10
    SYSTEM_TIME_CHANGED = 11
    INVALID_LICENSE_PARAMETERS = 12
    LICENSE_EXPIRED = 13
    ACTIVATION_TIMESPAN_EXPIRED = 14
    NO_SUBSCRIPTIONS = 15
    NO_ACTIVE_SUBSCRIPTIONS = 16
    CUSTOMER_TO_VENDOR_FILE_FAILED = 17
    VENDOR_TO_CUSTOMER_FILE_FAILED = 18
    GENERAL_ERROR = 0xFFFFFFFF


def get_version() -> str:
    from .__version__ import __version__
    return __version__


def check_license(product: str) -> ErrorCode:
    return GtecLicensingLib.check_license(product)


def refresh_license(product: str) -> ErrorCode:
    return GtecLicensingLib.refresh_license(product)


def get_activation_status(
    license_key: str,
    product: str,
    email: str
) -> Tuple[ErrorCode, Optional[dict]]:
    return GtecLicensingLib.get_activation_status(
        license_key,
        product,
        email
    )


def activate(
    license_key: str,
    product: str,
    email: str
) -> ErrorCode:
    return GtecLicensingLib.activate(
        license_key,
        product,
        email
    )


def deactivate(product: str) -> ErrorCode:
    return GtecLicensingLib.deactivate(product)


def get_licenses() -> Tuple[ErrorCode, List[dict]]:
    return GtecLicensingLib.get_licenses()
