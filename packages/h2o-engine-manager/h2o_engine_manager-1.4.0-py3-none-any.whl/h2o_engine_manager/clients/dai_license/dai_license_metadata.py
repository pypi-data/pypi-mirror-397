from dataclasses import dataclass
from datetime import date
from typing import Optional

from h2o_engine_manager.gen.model.type_date import TypeDate
from h2o_engine_manager.gen.model.v1_dai_license_metadata import V1DAILicenseMetadata


@dataclass
class DAILicenseMetadata:
    """DAI License Metadata containing information about the configured license.

    Attributes:
        license_version: License version.
        serial_number: License serial number.
        licensee_organization: Organization name of the licensee.
        licensee_email: Email of the licensee.
        licensee_user_id: User ID of the licensee.
        is_h2o_internal_use: Indicates if this is for H2O internal use.
        created_by_email: Email of the person who created the license.
        creation_date: Date when the license was created.
        product: Product name (e.g., "DriverlessAI").
        license_type: License type (e.g., "developer").
        expiration_date: Date when the license expires.
    """

    license_version: str = ""
    serial_number: int = 0
    licensee_organization: str = ""
    licensee_email: str = ""
    licensee_user_id: str = ""
    is_h2o_internal_use: bool = False
    created_by_email: str = ""
    creation_date: Optional[date] = None
    product: str = ""
    license_type: str = ""
    expiration_date: Optional[date] = None


def _convert_type_date_to_date(type_date: Optional[TypeDate]) -> Optional[date]:
    """Converts TypeDate to datetime.date.

    Args:
        type_date: TypeDate object with year, month, day fields.

    Returns:
        datetime.date instance, or None if type_date is None.
    """
    if type_date is None:
        return None
    return date(year=type_date.year, month=type_date.month, day=type_date.day)


def from_api_object(api_object: V1DAILicenseMetadata) -> DAILicenseMetadata:
    """Converts API object to DAILicenseMetadata.

    Args:
        api_object: Generated API object.

    Returns:
        DAILicenseMetadata instance.
    """
    return DAILicenseMetadata(
        license_version=api_object.license_version,
        serial_number=api_object.serial_number,
        licensee_organization=api_object.licensee_organization,
        licensee_email=api_object.licensee_email,
        licensee_user_id=api_object.licensee_user_id,
        is_h2o_internal_use=api_object.is_h2o_internal_use,
        created_by_email=api_object.created_by_email,
        creation_date=_convert_type_date_to_date(api_object.creation_date),
        product=api_object.product,
        license_type=api_object.license_type,
        expiration_date=_convert_type_date_to_date(api_object.expiration_date),
    )
