<p align="center">
  <img src="https://raw.githubusercontent.com/silentsokolov/dagster-hashicorp/main/docs/logo.jpg" alt="dagster-hashicorp logo" width="300"/>
</p>

[![build](https://github.com/silentsokolov/dagster-hashicorp/actions/workflows/build.yml/badge.svg)](https://github.com/silentsokolov/dagster-hashicorp/actions/workflows/build.yml) [![codecov](https://codecov.io/gh/silentsokolov/dagster-hashicorp/branch/main/graph/badge.svg?token=Pz2ptd7HYU)](https://codecov.io/gh/silentsokolov/dagster-hashicorp)

# dagster-hashicorp

A package for integrating [Hashicorp Vault](https://www.vaultproject.io/) with [Dagster](https://dagster.io/).

### Requirements

* Dagster 0.14+

### Installation

Use your favorite Python package manager to install the app from PyPI, e.g.

```bash
pip install dagster-hashicorp
```

# Usage Notes

## Vault

#### Auth method

- [x] Token
- [x] User / Password
- [x] Approle
- [x] Kubernetes

#### Example

```python
from dagster import build_op_context, job, op
from dagster_hashicorp.vault import vault_resource


@op(required_resource_keys={"vault"})
def example_vault_op(context):
    # Path of secret uses pattern <mount_point>/data/<path>

    # Read
    secret_data = context.resources.vault.read_secret(
        secret_path="secret/data/foo/bar"
    )
    context.log.debug(f"Secret: {secret_data}")

    # Write
    context.resources.vault.create_or_update_secret(
        secret_path="secret/data/foo/bar", {"bar": "foo"}
    )


@job(resource_defs={"vault": vault_resource})
def example_job():
    example_vault_op()


example_job.execute_in_process(
    run_config={
        "resources": {
            "vault": {
                "config": {
                    "url": "vault-host:8200",
                    "auth_type": {"token": {"token": "s.your-token"}},
                }
            }
        }
    }
)

# OR use environment variables

example_job.execute_in_process(
    run_config={
        "resources": {
            "vault": {
                "config": {
                    "url": "vault-host:8200",
                    "auth_type": {"token": {"token": {"env": "VAULT_TOKEN"}}},
                    # or
                    # "auth_type": {"userpass": {"username": {"env": "VAULT_USER"}, "password": {"env": "VAULT_PASS"}}},
                    # or
                    # "auth_type": {"approle": {"role_id": {"env": "VAULT_ROLE_ID"}, "secret_id": {"env": "VAULT_SECRET_ID"}}},
                    # or
                    # "auth_type": {"kubernetes": {"role": {"env": "VAULT_ROLE"}, "jwt_path": {"env": "VAULT_JWT_PATH"}}},
                }
            }
        }
    }
)
```
