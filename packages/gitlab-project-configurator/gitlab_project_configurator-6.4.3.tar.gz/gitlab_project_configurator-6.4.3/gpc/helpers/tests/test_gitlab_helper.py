# Third Party Libraries
import pytest

# Gitlab-Project-Configurator Modules
from gpc.helpers.gitlab_helper import is_bot_user_for_project_member


@pytest.mark.parametrize(
    "name, expected",
    [
        ("project_123_bot_abc123", True),
        ("project_130583_bot_a466d25997cbcf0ad32b9f7b378fede2", True),
        ("gitlab_security_policy_project_20589_bot_7f73ec2b2c61439c094c1dc3527a0cc2", True),
        ("project_123_bot", False),
        ("project_bot_abc123", False),
        ("project_123_abc123", False),
        ("123_bot_abc123", False),
        ("jean.claude", False),
    ],
)
def test_is_bot_user_for_project_member(name, expected):
    assert is_bot_user_for_project_member(name) == expected
