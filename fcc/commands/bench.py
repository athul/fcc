import sys
import click
import requests
import time
from fcc.utils.logs import get_logs_of_deploy

from rich.console import Console
from rich.table import Table

from fcc.utils.utils import (
    apps_to_update_menu,
    check_bench_for_updates,
    deploy_new_bench,
    get_bench_menu,
    get_bench_updated_apps,
    get_team_with_menu,
    TOKEN_AUTH_HEADER,
    humanify,
    validate_bench,
    validate_team,
)


@click.group(help="Access Benches and execute actions on Benches")
def bench():
    pass


@click.command("list", help="List all Private benches under a team")
@click.option("--team", help="Your Frappe Cloud team")
def get_benches(team):
    if not team:
        team = get_team_with_menu()
    benches_req = requests.post(
        "http://fc:8000/api/method/press.api.bench.all",
        headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
    )
    if benches_req.ok:
        try:
            all_benches = benches_req.json()
            benches_table = Table(
                "Bench Title",
                "Status",
                "Number of Sites",
                "Total Apps",
                "Version",
                "Bench Name",
                "Created",
                title=f"All Benches of {team}",
            )
            for bench in all_benches["message"]:
                benches_table.add_row(
                    bench["title"],
                    bench["status"],
                    str(bench["number_of_sites"]),
                    str(bench["number_of_apps"]),
                    bench["version"],
                    bench["name"],
                    humanify(bench["creation"]),
                )
            Console().print(benches_table)
        except Exception as e:
            print(e)


@click.command("deploy", help="Deploy a new version of the Bench")
@click.option("--team", help="Team owning the Private Bench")
@click.option("--bench", help="The Name of the bench. eg: bench-4219")
def deploy_bench(team, bench):
    if team:
        validate_team(team)
    if not team:
        team = get_team_with_menu()
    if not bench:
        bench = get_bench_menu(team)
        title = validate_bench(team, bench)
    else:
        import re

        b_name = re.compile("bench-[0-9]{4}")
        if not b_name.match(bench):
            sys.exit(1)
        title = validate_bench(team, bench)
    update, app = check_bench_for_updates(team, bench)
    if update:
        try:
            apps_list = get_bench_updated_apps(app)
            ignore_list = apps_to_update_menu(apps_list, title)
            candidate = deploy_new_bench(team, bench, ignore_list)
            time.sleep(2)
            get_logs_of_deploy(candidate)

        except Exception:
            click.secho(f"Failed to get Apps to Update", fg="red")
            sys.exit(1)


@click.command("logs")
@click.option("--bench")
def get_logs(bench):
    get_logs_of_deploy(bench)


bench.add_command(get_benches)
bench.add_command(deploy_bench)
bench.add_command(get_logs)
