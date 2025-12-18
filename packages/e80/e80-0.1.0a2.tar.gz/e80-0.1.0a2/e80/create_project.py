import click
from e80.lib.environment import CLIEnvironment
from e80.lib.project import read_project_config, write_project_config
from e80.lib.platform import PlatformClient
from e80.lib.user import get_auth_info


def create_project(env: CLIEnvironment):
    config = read_project_config()
    auth_info = get_auth_info(env)
    if auth_info is None:
        raise click.UsageError("You are not logged in! Please run 'eighty80 login'.")

    pc = PlatformClient(api_key=auth_info.auth_token, env=env)
    if config.project_slug is None:
        cr = pc.create_project(config)
        config.project_slug = cr.project_slug
        write_project_config(config)
        click.echo(f"Successfully created your project: {cr.project_slug}")
