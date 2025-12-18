import http
from datetime import date

import pytest

from h2o_engine_manager.clients.exception import CustomApiException


def test_get_dai_license_metadata(
    dai_license_client_super_admin,
    dai_license_secret_2019,
):
    """Test getting DAI license metadata from a configured secret."""
    metadata = dai_license_client_super_admin.get_dai_license_metadata()

    assert metadata is not None

    # Verify the license metadata matches the test license
    assert metadata.license_version == "1"
    assert metadata.serial_number == 35
    assert metadata.licensee_organization == "H2O.ai"
    assert metadata.licensee_email == "tomk@h2o.ai"
    assert metadata.licensee_user_id == "35"
    assert metadata.is_h2o_internal_use is True
    assert metadata.created_by_email == "tomk@h2o.ai"
    assert metadata.creation_date == date(2019, 6, 11)
    assert metadata.product == "DriverlessAI"
    assert metadata.license_type == "developer"
    assert metadata.expiration_date == date(2020, 1, 1)


def test_get_dai_license_metadata_missing_secret(
    dai_license_client_super_admin,
):
    """Test getting DAI license metadata when secret is not created."""
    with pytest.raises(CustomApiException) as exc:
        dai_license_client_super_admin.get_dai_license_metadata()
    assert exc.value.status == http.HTTPStatus.INTERNAL_SERVER_ERROR


def test_get_dai_license_metadata_invalid_license(
    dai_license_client_super_admin,
    dai_license_secret_invalid,
):
    """Test getting DAI license metadata when license data is invalid."""
    with pytest.raises(CustomApiException) as exc:
        dai_license_client_super_admin.get_dai_license_metadata()
    assert exc.value.status == http.HTTPStatus.INTERNAL_SERVER_ERROR