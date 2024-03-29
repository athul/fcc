from fcc.utils.utils import (
    get_sites,
    get_site_menu,
    get_team_with_menu,
    humanify,
)
import click

from rich.console import Console
from rich.table import Table

C = Console()


@click.group(help="Access Sites and Execute actions on Sites")
def sites():
    pass


@click.command("list", help="List the sites")
@click.option("--team", help="Frappe Cloud Team for sites")
def list_sites(team):
    if not team:
        team = get_team_with_menu()
    all_sites = get_sites(team)
    sites_table = Table(
        "Site Name",
        "Status",
        "Version",
        "Region" "Created",
        title=f"All Sites of {team}",
    )
    for site in all_sites:
        sites_table.add_row(
            site["name"],
            site["status"],
            site["version"],
            site["cluster"],
            humanify(site["creation"]),
        )
    Console().print(sites_table)


@click.command("overview", help="Overview of a Site")
@click.option("--team", help="Frappe Cloud Team for sites")
@click.option("--site", help="The Frappe Cloud Site")
def overview(team, site):
    if not team:
        team = get_team_with_menu()
    if not site:
        site = get_site_menu(team)

    print(site)
    print(team)
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.syntax import Syntax

    l = Layout(size=5)
    C = Console(height=10)
    l.split_column(Layout(name="Plan", size=5),
                   Layout(name="Activities", size=5))

    l["Plan"].update(Panel(Syntax(str(site), "json")))
    l["Activities"].update("Activities")

    C.print(l)


sites.add_command(list_sites)
