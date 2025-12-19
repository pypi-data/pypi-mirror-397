"""
test_update issues template
---------------------------
"""

# Third Party Libraries
from dictns import Namespace
from gitlab.v4.objects import Project  # pylint: disable=unused-import

# Gitlab-Project-Configurator Modules
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode
from gpc.project_rule_executor import ProjectRuleExecutor


# pylint: disable=redefined-outer-name, unused-argument, protected-access, duplicate-code


def test_update_issues_template(mocker, fake_gitlab, fake_project):
    # Mock
    mocker.patch("gpc.tests.test_project_ci_config_path.Project.save")
    mocker.patch(
        "gpc.tests.test_project_ci_config_path.ProjectRuleExecutor.project",
        mocker.PropertyMock(return_value=fake_project),
    )
    fake_project.issues_template = "old_issues_template"
    project_rules = Namespace(
        {
            "issues_template": "new_issues_template",
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, gql=mocker.Mock()
        ),
    )
    p.update_settings()

    assert p.get_changes_json() == [
        {
            "property_name": "issues_template",
            "differences": {
                "before": "old_issues_template",
                "after": "new_issues_template",
                "action": "updated",
            },
        },
    ]

    # Testing here that the issue template is not updated if issues_access_level is disabled:
    project_rules = Namespace(
        {
            "permissions": {"issues_access_level": "disabled"},
            "issues_template": "even_newer_issues_template",
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, gql=mocker.Mock()
        ),
    )
    p.update_settings()
    assert p.get_changes_json() == [
        {
            "property_name": "permissions",
            "differences": {
                "action": "updated",
                "before": {
                    "issues_access_level": "enabled",
                },
                "after": {
                    "issues_access_level": "disabled",
                },
            },
        },
    ]

    # Testing that the issue template is updated when issues are enabled again:
    project_rules = Namespace(
        {
            "permissions": {"issues_access_level": "enabled"},
            "issues_template": "even_newer_issues_template",
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, gql=mocker.Mock()
        ),
    )
    p.update_settings()
    assert p.get_changes_json() == [
        {
            "property_name": "issues_template",
            "differences": {
                "before": "new_issues_template",
                "after": "even_newer_issues_template",
                "action": "updated",
            },
        },
        {
            "property_name": "permissions",
            "differences": {
                "action": "updated",
                "before": {
                    "issues_access_level": "disabled",
                },
                "after": {
                    "issues_access_level": "enabled",
                },
            },
        },
    ]

    # We need to support both the deprecated issues_enabled as well as the new issues_access_level:
    # Testing here that the issue template is not updated if issues_enabled is false
    project_rules = Namespace(
        {
            "permissions": {"issues_enabled": False},
            "issues_template": "new_issue_template",
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, gql=mocker.Mock()
        ),
    )
    p.update_settings()
    assert p.get_changes_json() == [
        {
            "property_name": "permissions",
            "differences": {
                "action": "updated",
                "before": {
                    "issues_access_level": "enabled",
                },
                "after": {
                    "issues_access_level": "disabled",
                },
            },
        },
    ]

    # Testing that the issue template is updated when issues are enabled again:
    project_rules = Namespace(
        {
            "permissions": {"issues_enabled": True},
            "issues_template": "the_newest_template_ever",
        }
    )
    p = ProjectRuleExecutor(
        gl=fake_gitlab,
        project_path="fake/path/to/project",
        rule=project_rules,
        gpc_params=GpcParameters(
            config=mocker.Mock("fake_config"), mode=RunMode.APPLY, gql=mocker.Mock()
        ),
    )
    p.update_settings()
    assert p.get_changes_json() == [
        {
            "property_name": "issues_template",
            "differences": {
                "before": "even_newer_issues_template",
                "after": "the_newest_template_ever",
                "action": "updated",
            },
        },
        {
            "property_name": "permissions",
            "differences": {
                "action": "updated",
                "before": {
                    "issues_access_level": "disabled",
                },
                "after": {
                    "issues_access_level": "enabled",
                },
            },
        },
    ]
