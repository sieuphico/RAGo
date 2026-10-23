import pytest

from app.adapters.idp_fake import IdpFake
from app.core.config import get_settings
from app.core.wiring import build_idp


def test_fake_idp_refused_by_default() -> None:
    settings = get_settings().model_copy(update={"idp": "fake", "allow_fake_idp": False})
    with pytest.raises(RuntimeError, match="CWD_ALLOW_FAKE_IDP"):
        build_idp(settings)


def test_fake_idp_allowed_when_explicit() -> None:
    settings = get_settings().model_copy(update={"idp": "fake", "allow_fake_idp": True})
    assert isinstance(build_idp(settings), IdpFake)


def test_default_setting_is_closed() -> None:
    from app.core.config import Settings

    assert Settings.model_fields["allow_fake_idp"].default is False


def test_unknown_idp_not_implemented() -> None:
    settings = get_settings().model_copy(update={"idp": "oidc", "allow_fake_idp": True})
    with pytest.raises(NotImplementedError):
        build_idp(settings)
