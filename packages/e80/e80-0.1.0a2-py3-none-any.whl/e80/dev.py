import subprocess
import click
import json
import os

from e80.create_project import create_project
from e80.lib.project import read_project_config
from e80.lib.environment import CLIEnvironment
from e80.lib.user import get_auth_info
from e80.lib.platform import PlatformClient


def run_dev_server(env: CLIEnvironment, bind: str, port: int, reload: bool) -> None:
    create_project(env)

    config = read_project_config()
    auth_info = get_auth_info(env)
    if auth_info is None:
        raise click.UsageError("You are not logged in! Please run 'eighty80 login'.")
    pc = PlatformClient(api_key=auth_info.auth_token, env=env)

    click.echo(f"Fetching secrets for local development for: {config.project_slug}")
    secret_resp = pc.list_secrets_for_local(config)

    dev_env = os.environ.copy()
    dev_env.update(
        {
            "8080_PROJECT_SLUG": config.project_slug
            or "",  # project_slug should be populated from above.
            "8080_ORGANIZATION_SLUG": config.organization_slug,
            "8080_API_URL": env.api_host,
            "8080_PLATFORM_URL": env.platform_host,
            "8080_API_KEY": auth_info.auth_token,
            "8080_SECRETS_JSON": json.dumps(
                [s.model_dump() for s in secret_resp.secrets]
            ),
        }
    )

    command = [
        "uv",
        "run",
        "uvicorn",
        config.entrypoint,
        "--host",
        bind,
        "--port",
        str(port),
    ]
    if reload:
        command.append("--reload")

    subprocess.call(command, env=dev_env)
