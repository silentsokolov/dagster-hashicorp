from unittest import mock

import pytest

from dagster_hashicorp.vault.secrets import (
    ApproleAuth,
    KubernetesAuth,
    TokenAuth,
    UserpassAuth,
    Vault,
)


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_token(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200")
    client = vault.get_client()

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.is_authenticated.assert_called_once()

    assert client.token == "s.token"


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_token_as_path(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth(token_path="foo/bar/token"), url="localhost:8200")

    with mock.patch("builtins.open", mock.mock_open(read_data="secret_body")) as _:
        client = vault.get_client()

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.is_authenticated.assert_called_once()

    assert client.token == "secret_body"


def test_vault_token_without_args():
    with pytest.raises(Exception, match=r"This authentication requires 'token' or 'token_path'"):
        Vault(auth_type=TokenAuth(), url="localhost:8200")


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_userpass(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=UserpassAuth("user", "pass"),
        url="localhost:8200",
    )
    client = vault.get_client()

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.userpass.login.assert_called_once_with(username="user", password="pass")
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_userpass_mount_point(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=UserpassAuth("user", "pass"),
        url="localhost:8200",
        mount_point="secret",
    )
    client = vault.get_client()

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.userpass.login.assert_called_once_with(
        username="user", password="pass", mount_point="secret"
    )
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_approle(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=ApproleAuth("role", "secret"),
        url="localhost:8200",
    )
    client = vault.get_client()

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.approle.login.assert_called_once_with(role_id="role", secret_id="secret")
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_approle_mount_point(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=ApproleAuth("role", "secret"),
        url="localhost:8200",
        mount_point="secret",
    )
    client = vault.get_client()

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.approle.login.assert_called_once_with(
        role_id="role", secret_id="secret", mount_point="secret"
    )
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_kubernetes(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=KubernetesAuth("role"),
        url="localhost:8200",
    )
    with mock.patch("builtins.open", mock.mock_open(read_data="secret_body")) as mock_file:
        client = vault.get_client()

    mock_file.assert_called_with(
        "/var/run/secrets/kubernetes.io/serviceaccount/token", encoding="utf8"
    )

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.kubernetes.login.assert_called_once_with(role="role", jwt="secret_body")
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_kubernetes_mount_point(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=KubernetesAuth("role"),
        url="localhost:8200",
        mount_point="secret",
    )
    with mock.patch("builtins.open", mock.mock_open(read_data="secret_body")) as mock_file:
        client = vault.get_client()

    mock_file.assert_called_with(
        "/var/run/secrets/kubernetes.io/serviceaccount/token", encoding="utf8"
    )

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.kubernetes.login.assert_called_once_with(
        role="role",
        jwt="secret_body",
        mount_point="secret",
    )
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_kubernetes_pass_path(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(
        auth_type=KubernetesAuth("role", "foo/bar/path"),
        url="localhost:8200",
    )
    with mock.patch("builtins.open", mock.mock_open(read_data="secret_body")) as mock_file:
        client = vault.get_client()

    mock_file.assert_called_with("foo/bar/path", encoding="utf8")

    mock_hvac.Client.assert_called_with(url="localhost:8200", verify=True)
    client.auth.kubernetes.login.assert_called_once_with(
        role="role",
        jwt="secret_body",
    )
    client.is_authenticated.assert_called_once()


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_read_secret_invalid_path(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200")

    with pytest.raises(ValueError, match=r"Invalid secret path"):
        vault.read_secret("foo/bar/secret")


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_read_secret_kv2(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client
    expected_secret = {"secret_key": "secret_value"}
    mock_client.secrets.kv.v2.read_secret_version.return_value = {
        "request_id": "00000000-0000-0000-0000-000000000000",
        "lease_id": "",
        "renewable": False,
        "lease_duration": 0,
        "data": {
            "data": expected_secret,
            "metadata": {
                "created_time": "1970-01-01T00:00:00.0Z",
                "deletion_time": "",
                "destroyed": False,
                "version": 1,
            },
        },
    }

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200")

    secret = vault.read_secret(secret_path="secret/data/foo/bar")
    mock_client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        mount_point="secret", path="foo/bar", version=None
    )
    assert expected_secret == secret


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_read_secret_kv2_with_version(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200")

    vault.read_secret(secret_path="secret/data/foo/bar", secret_version=3)
    mock_client.secrets.kv.v2.read_secret_version.assert_called_once_with(
        mount_point="secret", path="foo/bar", version=3
    )


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_read_secret_kv1(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client
    expected_secret = {"secret_key": "secret_value"}
    mock_client.secrets.kv.v1.read_secret.return_value = {
        "request_id": "00000000-0000-0000-0000-000000000000",
        "lease_id": "",
        "renewable": False,
        "lease_duration": 1,
        "data": expected_secret,
    }

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200", kv_engine_version=1)

    secret = vault.read_secret(secret_path="secret/data/foo/bar")
    mock_client.secrets.kv.v1.read_secret.assert_called_once_with(
        mount_point="secret", path="foo/bar"
    )
    assert expected_secret == secret


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_read_secret_kv1_with_version(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200", kv_engine_version=1)

    with pytest.raises(ValueError, match=r"Only KV engine V2 can used the secret version"):
        vault.read_secret(secret_path="secret/data/foo/bar", secret_version=3)


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_create_or_update_secret_invalid_path(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200")

    with pytest.raises(ValueError, match=r"Invalid secret path"):
        vault.create_or_update_secret("foo/bar/secret", {"foo": "bar"})


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_create_or_update_secret_kv2(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200")

    vault.create_or_update_secret(
        secret_path="secret/data/foo/bar",
        secret={"foo": "bar"},
    )
    mock_client.secrets.kv.v2.create_or_update_secret.assert_called_once_with(
        path="foo/bar", secret={"foo": "bar"}, mount_point="secret"
    )


@mock.patch("dagster_hashicorp.vault.secrets.hvac")
def test_vault_create_or_update_secret_kv1(mock_hvac):
    mock_client = mock.MagicMock()
    mock_hvac.Client.return_value = mock_client

    vault = Vault(auth_type=TokenAuth("s.token"), url="localhost:8200", kv_engine_version=1)

    vault.create_or_update_secret(
        secret_path="secret/data/foo/bar",
        secret={"foo": "bar"},
    )
    mock_client.secrets.kv.v1.create_or_update_secret.assert_called_once_with(
        path="foo/bar", secret={"foo": "bar"}, mount_point="secret"
    )
