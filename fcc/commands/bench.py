import sys
import os
import click
import requests
import time
from fcc.utils.logs import get_logs_of_deploy
from fcc.utils.ssh import get_certificate, generate_certificate, login_to_bench

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
    get_site_menu,
    get_site,
    get_bench_from_group,
    get_ssh_enabled_for_bench,
    get_benches_with_sites_for_deploy,
    deploy_benches_and_sites
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
        "https://frappecloud.com/api/method/press.api.bench.all",
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
            ignore_list = apps_to_update_menu(apps_list)
            candidate = deploy_new_bench(team, bench, ignore_list)
            time.sleep(2)
            # connect_to_realtime_callback(candidate)
            get_logs_of_deploy(candidate)

        except Exception as e:
            click.secho(f"Failed to get Apps to Update", fg="red")
            print(e)
            sys.exit(1)


@click.command("logs")
@click.option("--bench")
def get_logs(bench):
    # connect_to_realtime_callback(bench)
    get_logs_of_deploy(bench)


@click.command("ssh", help="Login to Bench")
@click.option("--team", help="Team owning the Private Bench")
@click.option("--site", help="The Frappe Cloud Site")
# @click.option("--bench", help="The Name of the bench. eg: bench-4219")
def ssh_login(team, site):
    bench = None
    group = None
    if not team:
        team = get_team_with_menu()
    if not site:
        site = get_site_menu(team)
        group = site["group"]
        bench = site["bench"]
    if team or site:
        validate_team(team)
        # validate_bench(bench)
    if not bench:
        _site = get_site(site, team)
        group = _site["group"]
        bench = get_bench_from_group(site, group, team)

    title = validate_bench(team, group)
    ssh_check = get_ssh_enabled_for_bench(group, bench, team)
    if ssh_check["enabled"]:
        gen_certs = generate_certificate(group, team)
        if gen_certs:
            click.secho(f"Generating Certificates", fg="green")
        certificate = get_certificate(group, team)
        with open(os.path.expanduser("~/.ssh/id_sha2-cert.pub"), "w") as f:
            f.write(certificate["ssh_certificate"])
        click.secho(f"Logging into {title}", fg="blue")
        login_to_bench(bench, team, ssh_check["proxy"])
    else:
        click.secho(f"SSH is not enabled for {title}", fg="red")


@click.command("update", help="Update a Bench")
@click.option("--team", help="Team owning the Private Bench")
@click.option("--bench", help="The Name of the bench. eg: bench-4219")
def update_bench(team, bench):
    if team:
        validate_team(team)
    if not team:
        team = get_team_with_menu()
    if not bench:
        bench = get_bench_menu(team)
        validate_bench(team, bench)
    bnchsaps = get_benches_with_sites_for_deploy(team, bench) # weird variable naming I know
    deploy_benches_and_sites(team,bnchsaps["sites"],bnchsaps["ignored"],bench)


bench.add_command(get_benches)
bench.add_command(deploy_bench)
bench.add_command(get_logs)
bench.add_command(ssh_login)
bench.add_command(update_bench)
