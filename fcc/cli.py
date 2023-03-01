import click
import requests

from rich.console import Console
from rich.table import Table

from utils import generate_tokens,_token,get_team_with_menu

TOKEN_AUTH_HEADER = {"Authorization":f"Token {_token()}"}

@click.group()
def fcc():
    pass

@click.command()
@click.option("--username",prompt="Frappe Cloud Username",help="Username for Frappe Cloud")
@click.option("--password",prompt="Frappe Cloud Password",hide_input=True)
def login(username,password):
    print(username, password)
    creds = {"usr":username,"pwd":password}
    session = requests.Session()
    login = session.post("https://frappecloud.com/api/method/login",creds)
    if login.ok:
        click.secho("Authorization Successfull")
        generate_tokens(session=session)


@click.command()
def getme():
    try:
        me = requests.get("https://frappecloud.com/api/method/press.api.account.me",headers=TOKEN_AUTH_HEADER)
        if me.ok:
            click.secho(me.json(),fg="green")
    except:
        click.secho("Token Not found in fine", fg="red")

@click.command("sites")
@click.option("--team",help="Frappe Cloud Team for sites")
@click.option("--recents",help="Show only recent sites",is_flag=True,default=False)
@click.option("--all", help="Show all sites for the Team",is_flag=True,default=False)
def get_sites(team,recents,all):
    if not team:
        team = get_team_with_menu()
    sites_req = requests.post("https://frappecloud.com/api/method/press.api.site.all",headers={"Authorization":f"Token {_token()}","X-Press-Team":team})
    if sites_req.ok:
        all_sites =  sites_req.json()
        if recents:
            recents_table = Table("Site name", title=f"Recent Sites of {team}")
            print(all_sites["message"]["recents"])
            for site in all_sites["message"]["recents"]:
                recents_table.add_row(site)
            Console().print(recents_table)
        if all: 
            sites_table = Table("Site Name","Status","Version",title=f"All Sites of {team}")
            for site in all_sites["message"]["site_list"]:
                sites_table.add_row(site["name"],site["status"],site["version"])
            Console().print(sites_table)

@click.command("benches")
@click.option("--team",help="Frappe Cloud Team for sites")
def get_benches(team):
    if not team:
        team = get_team_with_menu()
    benches_req = requests.post("https://frappecloud.com/api/method/press.api.bench.all",headers={"Authorization":f"Token {_token()}","X-Press-Team":team})
    if benches_req.ok:
        try:
            all_benches = benches_req.json()
            benches_table = Table("Bench Title","Status","Number of Sites","Total Apps","Version","Bench Name",title=f"All Benches of {team}")
            for bench in all_benches["message"]:
                benches_table.add_row(bench["title"],bench["status"],str(bench["number_of_sites"]),str(bench["number_of_apps"]),bench["version"],bench["name"])
            Console().print(benches_table)
        except Exception as e:
            print(e)



fcc.add_command(login)
fcc.add_command(getme)
fcc.add_command(get_sites)
fcc.add_command(get_benches)

if __name__ == "__main__":
   fcc() 
