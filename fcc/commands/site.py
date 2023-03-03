import click
import requests

from rich.console import Console
from rich.table import Table


from fcc.utils.utils import get_team_with_menu,TOKEN_AUTH_HEADER

@click.group()
def sites():
    pass

@click.command("list")
@click.option("--team",help="Frappe Cloud Team for sites")
@click.option("--recents",help="Show only recent sites",is_flag=True,default=True)
@click.option("--all", help="Show all sites for the Team",is_flag=True)
def get_sites(team,recents,all):
    if not team:
        team = get_team_with_menu()
    header = {**TOKEN_AUTH_HEADER,"X-Press-Team":team}
    sites_req = requests.post("http://135.181.42.205:8000/api/method/press.api.site.all",headers=header)
    if sites_req.ok:
        all_sites =  sites_req.json()
        if recents:
            recents_table = Table("Site name", title=f"Recent Sites of {team}")
            for site in all_sites["message"]["recents"]:
                recents_table.add_row(site)
            Console().print(recents_table)
        if all: 
            sites_table = Table("Site Name","Status","Version",title=f"All Sites of {team}")
            for site in all_sites["message"]["site_list"]:
                sites_table.add_row(site["name"],site["status"],site["version"])
            Console().print(sites_table)

sites.add_command(get_sites)
