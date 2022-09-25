import click
from flask.cli import with_appcontext


@click.group()
def cli():
    """Main entry point"""


@cli.command("init")
@with_appcontext
def init():
    """Create a new admin user"""
    from vm.extensions import db
    from vm.models import User, Role
    click.echo("create role ADMIN, BUYER, SELLER")
    role_admin = Role(id=1, name="ADMIN")
    db.session.add(role_admin)
    role_buyer = Role(id=2, name="BUYER")
    db.session.add(role_buyer)
    role_seller = Role(id=3, name="SELLER")
    db.session.add(role_seller)

    click.echo("create user")

    user = User(username="admin",  password="admin", active=True, role_id=1)
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")


if __name__ == "__main__":
    cli()
