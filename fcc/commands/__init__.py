import click
from fcc.commands.bench import bench
from fcc.commands.site import sites
from fcc.commands.auth import login,getme

@click.group()
def fcc():
    """The FC CLI"""

fcc.add_command(sites)
fcc.add_command(bench)
fcc.add_command(login)
fcc.add_command(getme)

if __name__ == '__main__':
    fcc()
