import pytest
from xkid.lenses import registry


def test_defaults_and_casting_apply():
    # steps arrives as str from CLI; registry must coerce to int and apply defaults
    out = registry.lens_run("oscillation", {"steps": "8"})
    assert out["lens"] == "oscillation"
    assert out["params"]["steps"] == 8
    assert out["params"]["dim"] == 6  # default


def test_unknown_param_rejected():
    with pytest.raises(ValueError):
        registry.lens_run("oscillation", {"steps": 8, "nope": 1})


def test_digest_exactly_one_of_enforced():
    with pytest.raises(ValueError):
        registry.lens_run("digest", {"text": "hello", "hex": "00"})
    with pytest.raises(ValueError):
        registry.lens_run("digest", {})  # neither provided

    out = registry.lens_run("digest", {"text": "hello"})
    assert out["lens"] == "digest"
