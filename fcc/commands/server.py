import click
import requests

from rich.console import Console
from rich.table import Table


from fcc.utils.utils import get_team_with_menu,humanify,TOKEN_AUTH_HEADER

@click.group(help="Access Servers and Execute actions on Servers")
def servers():
    pass

@click.command("list",help="List the sites")
@click.option("--team",help="Frappe Cloud Team for sites")
@click.option("--recents",help="Show only recent sites",is_flag=True,default=True)
@click.option("--all", help="Show all sites for the Team",is_flag=True)
def get_servers(team,recents,all):
    if not team:
        team = get_team_with_menu()
    servers_req = requests.post("http://135.181.42.205:8000/api/method/press.api.server.all",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team})
    if servers_req.ok:
        try:
            all_servers = servers_req.json()
            servers_table = Table("Server Title","Status","App Server","Server Name","Created",title=f"All Servers of {team}")
            for server in all_servers["message"]:
                servers_table.add_row(server["title"],server["status"],server["app_server"],server["name"],humanify(server["creation"]))
            Console().print(servers_table)
        except Exception as e:
            print(e)

servers.add_command(get_servers)
