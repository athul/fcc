from typing import Dict
from requests.api import request
import click
import requests
import sys

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
    teams_req = requests.post("http://135.181.42.205:8000/api/method/press.api.account.get",headers={"Authorization":f"Token {_token()}"})
    if teams_req.ok:
        account_details = teams_req.json()["message"]
        teams = account_details["teams"]
        return teams
    else:
        click.secho("Failed to get available teams", fg="red")

def get_benches(team):
    benches_req = requests.post("http://135.181.42.205:8000/api/method/press.api.bench.all",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team})
    if benches_req.ok:
        benches = benches_req.json()["message"]
        return benches
        
def check_bench_for_updates(team,bench):
    data = {"name":bench}
    update_req = requests.post("http://135.181.42.205:8000/api/method/press.api.bench.deploy_information",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team},json=data)
    if update_req.ok:
        bench_info = update_req.json()["message"]
        if bench_info["update_available"]:
            return True, bench_info
        else:
            return False, bench_info

def get_bench_updated_apps(bench_info):
    apps = []
    for app in bench_info["apps"]:
        if app["update_available"]:
            # print(app)
            _app = {"title":app["title"],"c_hash":app["current_hash"],"n_hash":app["next_hash"],"name":app["app"]}
            apps.append(_app)
    return apps

def apps_to_update_menu(apps):
    apps_list = [f"{x['title']} : {x['c_hash'][:7]} -> {x['n_hash'][:7]}" for x in apps]
    # print(apps_list)
    apps_menu = TerminalMenu(apps_list,multi_select=True,show_multi_select_hint=True,title="Select the Apps you want to add in the new update")
    idx = apps_menu.show()
    ignore_list = []
    idx_list = [x for x in idx]
    diff_list = [x for x in range(len(apps))]
    missing = list(set(range(max(diff_list)+1)) - set(idx_list))
    for i in missing:
        ignore_list= apps[i]["name"]
    return ignore_list


def bench_menu(benches):
    all_bench_list = []
    for bench in benches: 
        all_bench_list.append(f"{bench['title']} : {bench['name']}")
    menu = TerminalMenu(all_bench_list,title="Select Bench you want to Deploy",show_search_hint=True)
    idx = menu.show()
    bench = all_bench_list[idx].split(":")[1].lstrip()
    return bench

def deploy_bench(team,bench,ignore_list):
    data = {"name":bench,"apps_to_ignore":ignore_list}
    deploy_req = requests.post("http://135.181.42.205:8000/api/method/press.api.bench.deploy",headers={**TOKEN_AUTH_HEADER,"X-Press-Team":team},json=data)
    if deploy_req.ok:
        candidate = deploy_req.json()["message"]
        print(f"Bench is being deployed, check progress at http://135.181.42.205:8000/dashboard/benches/{bench}/deploys/{candidate}")
        return candidate


def get_team_with_menu():
    """
    Generates a simple menu to select the team
    The Team data is received from the teams associated with the account
    using the API
    ref: get_team()

    """
    team_list = get_team()
    menu = TerminalMenu(team_list,title="Select Team")
    menu_index = menu.show()
    team = team_list[menu_index]
    return team

def get_bench_menu(team):
    benches = get_benches(team)
    bench_name = bench_menu(benches)
    update,app = check_bench_for_updates(team,bench_name)
    if update:
        apps_list = get_bench_updated_apps(app)
        ignore_list = apps_to_update_menu(apps_list)
        deploy_bench(team,bench_name,ignore_list)
        
    else:
        pass

