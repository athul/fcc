from typing import Tuple
import click
import requests
import sys
import humanize
from datetime import datetime as dt

from simple_term_menu import TerminalMenu

def generate_tokens(session:requests.Session):
    # TODO: Do file check and ask for prompts
    try:
        token_req = session.post("http://135.181.42.205:8000/api/method/press.api.account.create_api_secret")
        if token_req.ok:
            tokens = token_req.json()
            api_key = tokens["message"]["api_key"]
            api_secret = tokens["message"]["api_secret"]
            with open(".fcc","w") as f:
                f.write(f"{api_key}:{api_secret}")
            click.secho("Token Generated! and saved in .fcc file")

    except Exception as e:
        print(e)
        print("Failed to Fetch API tokens")

def _token() -> str:
    try:
        with open(".fcc") as f:
            return f.readline()
    except:
        click.secho("Token file not found, please execute fcc login to create the required credentials",fg="red")
        sys.exit(1)
        

TOKEN_AUTH_HEADER = {"Authorization":f"Token {_token()}"}

def get_team():
    try:
        teams_req = requests.post("http://135.181.42.205:8000/api/method/press.api.account.get",headers={"Authorization":f"Token {_token()}"})
        if teams_req.ok:
            account_details = teams_req.json()["message"]
            teams = account_details["teams"]
            return teams
        else:
            click.secho("Failed to get available teams", fg="red")
    except Exception as e:
        click.secho("Failed to get available teams",fg="yellow")
        click.secho(e,fg="red")
        sys.exit(1)

def validate_team(team):
    teams = get_team()
    if team not in teams:
        click.secho("Team Not Found in the account")
        sys.exit(1)
    else:
        return True

def get_benches(team):
    try:
        benches_req = requests.post("http://135.181.42.205:8000/api/method/press.api.bench.all",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team})
        if benches_req.ok:
            benches = benches_req.json()["message"]
            return benches
    except Exception as e:
        click.secho(f"\nFailed to get benches \n\n{e}",fg="yellow")
        sys.exit(1)
        
def check_bench_for_updates(team,bench):
    data = {"name":bench}
    try:
        update_req = requests.post("http://135.181.42.205:8000/api/method/press.api.bench.deploy_information",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team},json=data)
        if update_req.ok:
            bench_info = update_req.json()["message"]
            if bench_info["update_available"]:
                return True, bench_info
            else:
                click.secho(f"\nNo Apps to Update on Bench {bench}",fg="yellow")
                return False, bench_info
    except Exception as e:
        click.secho(f"\nRequest Failed to  get updates on Benches\n\n{e}",fg="yellow")
        sys.exit(1)

def get_bench_updated_apps(bench_info):
    apps = []
    for app in bench_info["apps"]:
        if app["update_available"]:
            apps.append(app)
    return apps

def apps_to_update_menu(apps,bench):
    apps_list = [f"{x['title']} : {x['current_hash'][:7]} -> {x['next_hash'][:7]}" for x in apps]
    try:
        apps_menu = TerminalMenu(apps_list,multi_select=True,show_multi_select_hint=True,title=f"Select the Apps you want to add in the new update of {bench}")
        idx:Tuple[int] = apps_menu.show()
        ignore_list = []
        idx_list = [x for x in idx]
        diff_list = [x for x in range(len(apps))]
        missing = list(set(range(max(diff_list)+1)) - set(idx_list))
        for i in missing:
            ignore_list.append(apps[i])
        return ignore_list
    except Exception as e:
        sys.exit(1)



def deploy_new_bench(team,bench,ignore_list):
    data = {"name":bench,"apps_to_ignore":ignore_list}
    try:
        deploy_req = requests.post("http://135.181.42.205:8000/api/method/press.api.bench.deploy",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team},json=data)
        if deploy_req.ok:
            candidate = deploy_req.json()["message"]
            click.secho(f"\nBench is being deployed, check progress at http://135.181.42.205:8000/dashboard/benches/{bench}/deploys/{candidate}",fg="green")
            return candidate
        elif deploy_req.status_code == 417:
            click.secho(f"\nAnother version of this bench is already being deployed",fg="yellow")
    except Exception as e:
        click.secho(f"Error for Update\n\n{e}",fg="red")
        sys.exit(1)


def get_team_with_menu():
    """
    Generates a simple menu to select the team
    The Team data is received from the teams associated with the account
    using the API
    ref: get_team()

    """
    team_list = get_team()
    try:
        menu = TerminalMenu(team_list,title="Select Team")
        menu_index = menu.show()
        team = team_list[menu_index]
        return team
    except:
        sys.exit(1)

def get_bench_menu(team):
    benches = get_benches(team)
    all_bench_list = []
    for bench in benches: 
        all_bench_list.append(f"{bench['title']} : {bench['name']}")
    try:
        menu = TerminalMenu(all_bench_list,title="Select Bench you want to Deploy",show_search_hint=True)
        idx = menu.show()
        bench = all_bench_list[idx].split(":")[1].lstrip()
        return bench
    except:
        sys.exit(1)

def validate_bench(team,bench_name):
    benches = get_benches(team)
    title = ""
    for b in benches:
        if b["name"] == bench_name:
            title= b["title"]
    if len(title) == 0:
        click.secho("Bench Not found in the provided Team")
        sys.exit(1)
    else:
        return title

def humanify(time):
    return humanize.naturaldelta(dt.now() - dt.strptime(time,"%Y-%m-%d %H:%M:%S.%f"))
