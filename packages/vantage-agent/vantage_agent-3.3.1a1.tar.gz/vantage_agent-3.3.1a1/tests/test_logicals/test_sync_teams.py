"""Tests for syncing Keycloak teams with SSSD."""

import json
from subprocess import CalledProcessError
from textwrap import dedent
from unittest import mock

import pytest
from respx.router import MockRouter

from vantage_agent.logicals.sync_teams import (
    _build_ldap_filter,
    _extract_org_id_from_filter,
    _resolve_org_id,
    create_backup,
    get_cluster_teams,
    reload_sssd,
    sync_cluster_teams,
    update_sssd_access_filter,
)
from vantage_agent.settings import SETTINGS


@mock.patch("vantage_agent.logicals.sync_teams.copyfile")
def test_create_backup(copyfile_mock: mock.Mock):
    """Ensure a backup file is created alongside the original."""
    file_path = "/etc/sssd/sssd.conf"

    create_backup(file_path)

    copyfile_mock.assert_called_once_with(file_path, f"{SETTINGS.CACHE_DIR}/sssd.conf.bkp")


@pytest.mark.parametrize(
    "filter_value,expected_org_id",
    [
        (
            "(|(memberOf=cn=slurm-users,ou=Groups,ou=org-123,ou=organizations,dc=vantagecompute,dc=ai))",
            "org-123",
        ),
        ("(memberOf=cn=slurm-users,ou=Groups,dc=vantagecompute,dc=ai)", None),
    ],
)
def test_extract_org_id_from_filter(filter_value: str, expected_org_id: str | None):
    """Extract the org_id from the ldap_access_filter value."""
    assert _extract_org_id_from_filter(filter_value) == expected_org_id


def test_build_ldap_filter_adds_slurm_group_and_sorts_teams():
    """Always include slurm-users and sort unique team names."""
    org_id = "org-abc"
    team_names = ["team-two", "team-one", "team-two", ""]

    filter_value = _build_ldap_filter(org_id, team_names)

    assert filter_value == (
        "(|"
        "(memberOf=cn=slurm-users,ou=Groups,ou=org-abc,ou=organizations,dc=vantagecompute,dc=ai)"
        "(memberOf=cn=team-one,ou=Teams,ou=org-abc,ou=organizations,dc=vantagecompute,dc=ai)"
        "(memberOf=cn=team-two,ou=Teams,ou=org-abc,ou=organizations,dc=vantagecompute,dc=ai)"
        ")"
    )


def test_resolve_org_id_prefers_team_payload():
    """Return org_id from teams before falling back to sssd.conf."""
    teams = [{"organization": "team-org"}, {"organization": "other-org"}]
    sssd_lines = [
        "ldap_access_filter = (|(memberOf=cn=slurm-users,ou=Groups,ou=sssd-org,ou=organizations,dc=vantagecompute,dc=ai))"  # noqa
    ]

    assert _resolve_org_id(teams, sssd_lines) == "team-org"


def test_resolve_org_id_from_sssd_lines_when_missing_in_teams():
    """Extract org_id from the existing ldap_access_filter line."""
    teams = [{"organization": None}, {}]
    sssd_lines = [
        "ldap_access_filter = (|(memberOf=cn=slurm-users,ou=Groups,ou=sssd-org,ou=organizations,dc=vantagecompute,dc=ai))\n"  # noqa
    ]

    assert _resolve_org_id(teams, sssd_lines) == "sssd-org"


def test_resolve_org_id_returns_none_when_not_found():
    """Return None when neither the payload nor sssd.conf contains org_id."""
    assert _resolve_org_id([], ["# no ldap_access_filter here\n"]) is None

@mock.patch("vantage_agent.logicals.sync_teams.create_backup")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
def test_update_sssd_access_filter_updates_existing_line(
    settings_mock: mock.Mock,
    create_backup_mock: mock.Mock,
    tmp_path
):
    """Replace an existing ldap_access_filter entry."""
    sssd_conf_path = tmp_path / "sssd.conf"
    settings_mock.SSSD_CONF_PATH = sssd_conf_path
    settings_mock.CACHE_DIR = tmp_path
    sssd_lines = [
        "[sssd]\n",
        "ldap_access_filter = (|(memberOf=cn=slurm-users,ou=Groups,ou=old,ou=organizations,dc=vantagecompute,dc=ai))\n",  # noqa
    ]

    updated = update_sssd_access_filter("org-1", ["team-b", "team-a"], sssd_lines)

    expected_line = f"ldap_access_filter = {_build_ldap_filter('org-1', ['team-b', 'team-a'])}\n"
    with open(sssd_conf_path, "r") as f:
        lines = f.readlines()

    assert updated is True
    assert lines == ["[sssd]\n", expected_line]
    create_backup_mock.assert_called_once_with(settings_mock.SSSD_CONF_PATH)


@mock.patch("vantage_agent.logicals.sync_teams.create_backup")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
def test_update_sssd_access_filter_appends_when_missing(
    settings_mock: mock.Mock, create_backup_mock: mock.Mock, tmp_path
):
    """Append ldap_access_filter when it is missing."""
    sssd_conf_path = tmp_path / "sssd.conf"
    settings_mock.SSSD_CONF_PATH = sssd_conf_path
    settings_mock.CACHE_DIR = tmp_path
    sssd_lines = ["[sssd]\n"]

    updated = update_sssd_access_filter("org-2", ["team-a"], sssd_lines)

    expected_line = f"ldap_access_filter = {_build_ldap_filter('org-2', ['team-a'])}\n"
    with open(sssd_conf_path, "r") as f:
        lines = f.readlines()

    assert updated is True
    assert lines == ["[sssd]\n", expected_line]
    create_backup_mock.assert_called_once_with(settings_mock.SSSD_CONF_PATH)


@mock.patch("vantage_agent.logicals.sync_teams.create_backup")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
def test_update_sssd_access_filter_returns_false_when_no_change(
    settings_mock: mock.Mock, create_backup_mock: mock.Mock, tmp_path
):
    """Do not rewrite the file if the filter is already up to date."""
    sssd_conf_path = tmp_path / "sssd.conf"
    settings_mock.SSSD_CONF_PATH = sssd_conf_path
    settings_mock.CACHE_DIR = tmp_path
    existing_line = f"ldap_access_filter = {_build_ldap_filter('org-3', ['team-a'])}\n"

    sssd_conf_path.write_text(existing_line)
    sssd_lines = [existing_line]

    updated = update_sssd_access_filter("org-3", ["team-a"], sssd_lines)

    assert updated is False
    assert sssd_conf_path.read_text() == existing_line
    create_backup_mock.assert_called_once_with(settings_mock.SSSD_CONF_PATH)


@pytest.mark.respx(base_url=str(SETTINGS.BASE_API_URL))
@pytest.mark.usefixtures("mock_access_token")
async def test_get_cluster_teams(respx_mock: MockRouter):
    """Fetch teams for the current cluster via GraphQL."""
    query = dedent(
        """
        query($clusterId: String!) {
            teamsByCluster(clusterId: $clusterId) {
                id
                name
                organization
            }
        }
        """
    )
    body = {"query": query, "variables": {"clusterId": SETTINGS.OIDC_CLIENT_ID}}
    teams = [
        {"id": "1", "name": "alpha", "organization": "org-1"},
        {"id": "2", "name": "beta", "organization": "org-1"},
    ]
    respx_mock.post("/teams/graphql", json=body).respond(
        status_code=200, content=json.dumps({"data": {"teamsByCluster": teams}})
    )

    response = await get_cluster_teams()

    assert response == teams


@mock.patch("vantage_agent.logicals.sync_teams.update_sssd_access_filter")
@mock.patch("vantage_agent.logicals.sync_teams.get_cluster_teams")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
async def test_sync_cluster_teams_updates_filter(
    settings_mock: mock.Mock,
    get_cluster_teams_mock: mock.Mock,
    update_sssd_access_filter_mock: mock.Mock,
    tmp_path,
):
    """Happy path: read sssd.conf, resolve org_id, and update the filter."""
    sssd_conf_path = tmp_path / "sssd.conf"
    settings_mock.SSSD_CONF_PATH = sssd_conf_path
    sssd_filter_line = (
        "ldap_access_filter = (|(memberOf=cn=slurm-users,ou=Groups,ou=old,ou=organizations,dc=vantagecompute,dc=ai))\n"  # noqa
    )
    sssd_conf_path.write_text(sssd_filter_line)

    teams = [
        {"id": "1", "name": "alpha", "organization": "org-xyz"},
        {"id": "2", "name": "beta", "organization": "org-xyz"},
    ]
    get_cluster_teams_mock.return_value = teams

    await sync_cluster_teams()

    get_cluster_teams_mock.assert_called_once_with()
    update_sssd_access_filter_mock.assert_called_once_with(
        org_id="org-xyz",
        team_names=["alpha", "beta"],
        sssd_lines=[sssd_filter_line],
    )


@mock.patch("vantage_agent.logicals.sync_teams.logger")
@mock.patch("vantage_agent.logicals.sync_teams.get_cluster_teams")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
async def test_sync_cluster_teams_logs_missing_sssd_file(
    settings_mock: mock.Mock, get_cluster_teams_mock: mock.Mock, logger_mock: mock.Mock, tmp_path
):
    """Log an error when sssd.conf cannot be found."""
    settings_mock.SSSD_CONF_PATH = tmp_path / "missing.conf"
    get_cluster_teams_mock.return_value = []

    await sync_cluster_teams()

    logger_mock.error.assert_called_once_with(
        "SSSD configuration file not found at %s", settings_mock.SSSD_CONF_PATH
    )


@mock.patch("vantage_agent.logicals.sync_teams.logger")
@mock.patch("vantage_agent.logicals.sync_teams.update_sssd_access_filter")
@mock.patch("vantage_agent.logicals.sync_teams.get_cluster_teams")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
async def test_sync_cluster_teams_logs_unexpected_errors(
    settings_mock: mock.Mock,
    get_cluster_teams_mock: mock.Mock,
    update_sssd_access_filter_mock: mock.Mock,
    logger_mock: mock.Mock,
    tmp_path,
):
    """Capture unexpected exceptions while syncing teams."""
    settings_mock.SSSD_CONF_PATH = tmp_path / "sssd.conf"
    settings_mock.CACHE_DIR = tmp_path
    sssd_filter_line = (
        "ldap_access_filter = (|(memberOf=cn=slurm-users,ou=Groups,ou=existing,ou=organizations,dc=vantagecompute,dc=ai))\n"  # noqa
    )
    settings_mock.SSSD_CONF_PATH.write_text(sssd_filter_line)

    get_cluster_teams_mock.return_value = [{"id": "1", "name": "alpha", "organization": "org-1"}]
    update_sssd_access_filter_mock.side_effect = RuntimeError("unexpected boom")

    await sync_cluster_teams()

    update_sssd_access_filter_mock.assert_called_once()
    logger_mock.error.assert_called_once_with("Error while syncing teams to SSSD: unexpected boom")

@mock.patch("vantage_agent.logicals.sync_teams.subprocess.run")
def test_reload_sssd__test_the_success_execution(subprocess_run_mock: mock.Mock):
    """Reload the sssd to get the new changes in the sssd.conf."""
    reload_sssd()
    subprocess_run_mock.assert_called_once_with(
        [
                "systemctl", "stop", "sssd", "&&",
                "sss_cache", "-E", "&&",
                "rm", "-rf", "/var/lib/sss/db/*", "&&",
                "rm", "-rf", "/var/lib/sss/mc/*", "&&",
                "systemctl", "restart", "sssd"
            ], check=True, capture_output=True, text=True
    )

@mock.patch("vantage_agent.logicals.sync_teams.subprocess.run")
def test_reload_sssd__test_the_filed_execution(subprocess_run_mock: mock.Mock):
    """Reload the SSSD to get the new changes in the sssd.conf."""
    subprocess_run_mock.side_effect = CalledProcessError(
        stderr="Dummy Error", output="Log......", returncode=1, cmd=""
    )

    try:
        reload_sssd()
        assert False
    except Exception as e:
        subprocess_run_mock.assert_called_once_with(
            [
                "systemctl", "stop", "sssd", "&&",
                "sss_cache", "-E", "&&",
                "rm", "-rf", "/var/lib/sss/db/*", "&&",
                "rm", "-rf", "/var/lib/sss/mc/*", "&&",
                "systemctl", "restart", "sssd"
            ], check=True, capture_output=True, text=True
        )
        assert isinstance(e, CalledProcessError)


@mock.patch("vantage_agent.logicals.sync_teams.reload_sssd")
@mock.patch("vantage_agent.logicals.sync_teams.update_sssd_access_filter")
@mock.patch("vantage_agent.logicals.sync_teams.get_cluster_teams")
@mock.patch("vantage_agent.logicals.sync_teams.SETTINGS")
async def test_sync_cluster_teams_returns_when_org_id_missing(
    settings_mock: mock.Mock,
    get_cluster_teams_mock: mock.Mock,
    update_sssd_access_filter_mock: mock.Mock,
    reload_sssd_mock: mock.Mock,
    tmp_path,
):
    """Abort when org_id cannot be resolved."""
    sssd_conf_path = tmp_path / "sssd.conf"
    settings_mock.SSSD_CONF_PATH = sssd_conf_path
    sssd_conf_path.write_text("# empty file\n")

    get_cluster_teams_mock.return_value = [{"id": "1", "name": "lonely", "organization": None}]

    await sync_cluster_teams()

    get_cluster_teams_mock.assert_called_once_with()
    update_sssd_access_filter_mock.assert_not_called()
    reload_sssd_mock.assert_not_called()
