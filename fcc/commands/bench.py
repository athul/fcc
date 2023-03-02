import click
import requests

from rich.console import Console
from rich.table import Table

from fcc.utils.utils import get_team_with_menu,TOKEN_AUTH_HEADER 

@click.group()
def bench():
    pass

@click.command("list")
@click.option("--team",help="Frappe Cloud Team for sites")
def get_benches(team):
    if not team:
        team = get_team_with_menu()
    benches_req = requests.post("https://frappecloud.com/api/method/press.api.bench.all",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team})
    if benches_req.ok:
        try:
            all_benches = benches_req.json()
            benches_table = Table("Bench Title","Status","Number of Sites","Total Apps","Version","Bench Name",title=f"All Benches of {team}")
            for bench in all_benches["message"]:
                benches_table.add_row(bench["title"],bench["status"],str(bench["number_of_sites"]),str(bench["number_of_apps"]),bench["version"],bench["name"])
            Console().print(benches_table)
        except Exception as e:
            print(e)

bench.add_command(get_benches)
