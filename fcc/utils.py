import click
import requests

from simple_term_menu import TerminalMenu

def generate_tokens(session:requests.Session):
    try:
        token_req = session.post("https://frappecloud.com/api/method/press.api.account.create_api_secret")
        if token_req.ok:
            tokens = token_req.json()
            print(tokens)
            api_key = tokens["message"]["api_key"]
            api_secret = tokens["message"]["api_secret"]
            print(f"{api_key}:{api_secret}")
            with open(".fcc","w") as f:
                f.write(f"{api_key}:{api_secret}")
            click.secho("Token Generated! and saved in .fcc file")

    except Exception as e:
        print(e)
        print("Failed to Fetch API tokens")

def _token() -> str:
    with open(".fcc") as f:
        return f.readline()

def get_team():
    teams_req = requests.post("https://frappecloud.com/api/method/press.api.account.get",headers={"Authorization":f"Token {_token()}"})
    if teams_req.ok:
        account_details = teams_req.json()["message"]
        teams = account_details["teams"]
        return teams
    else:
        click.secho("Failed to get available teams", fg="red")

def get_team_with_menu() -> str:
        team_list = get_team()
        menu = TerminalMenu(team_list,title="Select Team")
        menu_index = menu.show()
        team = team_list[menu_index]
        return team
