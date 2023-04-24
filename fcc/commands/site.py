import click
import requests

from rich.console import Console
from rich.table import Table

C = Console()

from fcc.utils.utils import get_site_menu, get_team_with_menu, humanify, TOKEN_AUTH_HEADER


@click.group(help="Access Sites and Execute actions on Sites")
def sites():
    pass


@click.command("list", help="List the sites")
@click.option("--team", help="Frappe Cloud Team for sites")
@click.option("--recents", help="Show only recent sites", is_flag=True, default=True)
@click.option("--all", help="Show all sites for the Team", is_flag=True)
def get_sites(team, recents, all):
    if not team:
        team = get_team_with_menu()
    header = {**TOKEN_AUTH_HEADER, "X-Press-Team": team}
    try:
        sites_req = requests.post(
            "http://fc:8000/api/method/press.api.site.all", headers=header
        )
        if sites_req.ok:
            all_sites = sites_req.json()
            if recents:
                recents_table = Table(
                    "Site name", title=f"Recent Sites of {team}")
                for site in all_sites["message"]["recents"]:
                    recents_table.add_row(site)
                Console().print(recents_table)
            if all:
                sites_table = Table(
                    "Site Name",
                    "Status",
                    "Version",
                    "Created",
                    title=f"All Sites of {team}",
                )
                for site in all_sites["message"]["site_list"]:
                    sites_table.add_row(
                        site["name"],
                        site["status"],
                        site["version"],
                        humanify(site["creation"]),
                    )
                Console().print(sites_table)
    except Exception as e:
        print(e)
        click.secho(
            "Not Able to get sites list. please check your connection", fg="yellow"
        )
@click.command("overview", help="Overview of a Site")
@click.option("--team", help="Frappe Cloud Team for sites")
@click.option("--site", help="The Frappe Cloud Site")
def overview(team,site):
    if not team:
        team = get_team_with_menu()
    if not site:
        site = get_site_menu(team)
    
    # print(site)
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.syntax import Syntax
    l = Layout(size=5)
    C = Console(height=10)
    l.split_column(
            Layout(name="Plan",size=5),
            Layout(name="Activities",size=5)
    )

    l["Plan"].update(Panel(Syntax(str(site),"json")))
    # l["Activities"].update("Activities")

    C.print(l)


sites.add_command(get_sites)
sites.add_command(overview)
