from typing import Tuple
import click
import requests
import sys
import os
import humanize
from datetime import datetime as dt

from simple_term_menu import TerminalMenu


def generate_tokens(session: requests.Session):
    # TODO: Do file check and ask for prompts
    try:
        token_req = session.post(
            "https://frappecloud.com/api/method/press.api.account.create_api_secret"
        )
        if token_req.ok:
            tokens = token_req.json()
            api_key = tokens["message"]["api_key"]
            api_secret = tokens["message"]["api_secret"]
            home_dir = os.path.expanduser("~")
            with open(home_dir + "/.config/fcc/.fcc", "w") as f:
                f.write(f"{api_key}:{api_secret}")
            click.secho("Token Generated! and saved in .fcc file")

    except Exception as e:
        print(e)
        print("Failed to Fetch API tokens")


def _token() -> str:
    try:
        with open(os.path.expanduser("~") + "/.config/fcc/.fcc") as f:
            token = f.readline()
            return token
    except:
        click.secho(
            "Token file not found, please execute fcc login to create the required credentials",
            fg="red",
        )
        sys.exit(1)


TOKEN_AUTH_HEADER = {"Authorization": f"Token {_token()}"}


def get_team():
    try:
        teams_req = requests.post(
            "https://frappecloud.com/api/method/press.api.account.get",
            headers=TOKEN_AUTH_HEADER,
        )
        teams_req.raise_for_status()
        if teams_req.ok:
            teams = []
            account_details = teams_req.json()["message"]
            team_members = account_details["teams"]
            for member in team_members:
                teams.append(member["name"])
            return teams
        else:
            click.secho("Failed to get available teams", fg="red")
    except Exception as e:
        click.secho("Failed to get available teams", fg="yellow")
        click.secho(e, fg="red")
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
        benches_req = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.all",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
        )
        if benches_req.ok:
            benches = benches_req.json()["message"]
            return benches
    except Exception as e:
        click.secho(f"\nFailed to get benches \n\n{e}", fg="yellow")
        sys.exit(1)


def get_sites(team):
    try:
        sites_req = requests.post(
            "https://frappecloud.com/api/method/press.api.site.all",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
        )
        if sites_req.ok:
            sites = sites_req.json()["message"]
            return sites
    except Exception as e:
        click.secho(f"\nFailed to get Sites\n\n{e}", fg="yellow")


def get_site(site, team) -> dict:
    data = {"name": site}
    try:
        site_req = requests.post(
            "https://frappecloud.com/api/method/press.api.site.get",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if site_req.ok:
            _site = site_req.json()["message"]
            return _site
    except Exception as e:
        click.secho(f"\nFailed to get Site Details\n\n{e}", fg="yellow")


def check_bench_for_updates(team, bench):
    data = {"name": bench}
    try:
        update_req = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.deploy_information",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if update_req.ok:
            bench_info = update_req.json()["message"]
            if bench_info["update_available"]:
                return True, bench_info
            else:
                click.secho(f"\nNo Apps to Update on Bench {bench}", fg="yellow")
                return False, bench_info
    except Exception as e:
        click.secho(f"\nRequest Failed to  get updates on Benches\n\n{e}", fg="yellow")
        sys.exit(1)


def get_bench_updated_apps(bench_info):
    apps = []
    for app in bench_info["apps"]:
        if app["update_available"]:
            apps.append(app)
    return apps


def apps_to_update_menu(apps, bench):
    apps_list = [
        f"{x['title']} : {x['current_hash'][:7]} -> {x['next_hash'][:7]}" for x in apps
    ]
    try:
        apps_menu = TerminalMenu(
            apps_list,
            multi_select=True,
            show_multi_select_hint=True,
            title=f"Select the Apps you want to add in the new update of {bench}",
        )
        idx: Tuple[int] = apps_menu.show()
        ignore_list = []
        idx_list = [x for x in idx]
        diff_list = [x for x in range(len(apps))]
        missing = list(set(range(max(diff_list) + 1)) - set(idx_list))
        for i in missing:
            ignore_list.append(apps[i])
        return ignore_list
    except Exception as e:
        sys.exit(1)


def deploy_new_bench(team, bench, ignore_list):
    data = {"name": bench, "apps_to_ignore": ignore_list}
    try:
        deploy_req = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.deploy",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if deploy_req.ok:
            candidate = deploy_req.json()["message"]
            click.secho(
                f"\nBench is being deployed, check progress at https://frappecloud.com/dashboard/benches/{bench}/deploys/{candidate}",
                fg="green",
            )
            return candidate
        elif deploy_req.status_code == 417:
            click.secho(
                f"\nAnother version of this bench is already being deployed",
                fg="yellow",
            )
            sys.exit(1)
    except Exception as e:
        click.secho(f"Error for Update\n\n{e}", fg="red")
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
        menu = TerminalMenu(team_list, title="Select Team")
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
        menu = TerminalMenu(all_bench_list, title="Select Bench", show_search_hint=True)
        idx = menu.show()
        bench = all_bench_list[idx].split(":")[1].lstrip()
        return bench
    except:
        sys.exit(1)


def get_site_menu(team):
    sites = get_sites(team)
    all_sites = []
    for site in sites:
        all_sites.append(f"{site['name']} - {site['status']}")
    try:
        menu = TerminalMenu(all_sites, title="Select Site", show_search_hint=True)
        idx = menu.show()
        return sites[idx]
    except:
        sys.exit(1)


def validate_bench(team, bench_name):
    benches = get_benches(team)
    title = ""
    for b in benches:
        if b["name"] == bench_name:
            print(b["name"])
            title = b["title"]
    if len(title) == 0:
        click.secho("Bench Not found in the provided Team")
        sys.exit(1)
    else:
        return title


def humanify(time):
    return humanize.naturaldelta(dt.now() - dt.strptime(time, "%Y-%m-%d %H:%M:%S.%f"))


def get_bench_from_group(site, group, team):
    data = {"name": group}
    try:
        bench_versions = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.versions",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if bench_versions.ok:
            bench_versions = bench_versions.json()["message"]
            for bench in bench_versions:
                for _site in bench["sites"]:
                    if _site["name"] == site:
                        return bench["name"]
    except Exception as e:
        click.secho(f"Error fetching Bench\n\n{e}", fg="red")
        sys.exit(1)


def get_ssh_enabled_for_bench(group, bench, team) -> dict | None:
    data = {"name": group}
    try:
        ssh_enabled = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.versions",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if ssh_enabled.ok:
            benches = ssh_enabled.json()["message"]
            for _bench in benches:
                if _bench["name"] == bench:
                    if _bench["is_ssh_proxy_setup"]:
                        return {"enabled": True, "proxy": _bench["proxy_server"]}
    except Exception as e:
        click.secho(f"Error fetching Bench\n\n{e}", fg="red")
        sys.exit(1)
