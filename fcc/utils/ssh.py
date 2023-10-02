import requests
import click
import os
import sys
from fcc.utils.utils import TOKEN_AUTH_HEADER


def generate_certificate(group, team) -> bool:
    data = {"name": group}
    try:
        certs_req = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.generate_certificate",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if certs_req.ok:
            click.secho("New Certificate Generated Successfully", fg="green")
            return True
        else:
            return False
            click.secho("Failed to generate SSH Certificate", fg="yellow")
            print(certs_req.text)
            sys.exit(1)
    except Exception as e:
        click.secho(f"\nFailed to generate SSH Certificate\n\n{e}", fg="red")
        sys.exit(1)


def get_certificate(group, team) -> dict:
    data = {"name": group}
    try:
        certs_req = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.certificate",
            headers={**TOKEN_AUTH_HEADER, "X-Press-Team": team},
            json=data,
        )
        if certs_req.ok:
            return certs_req.json()["message"]
        else:
            click.secho("Failed to get SSH Certificate", fg="yellow")
            print(certs_req.text)
            sys.exit(1)
    except Exception as e:
        click.secho(f"\nFailed to get SSH Certificate\n\n{e}", fg="red")
        print(e)
        sys.exit(1)


def login_to_bench(bench, team, proxy):
    import subprocess

    # ssh bench-4219-000004-f4-mumbai@n1-mumbai.frappe.cloud -p 2222
    subprocess.run(["ssh", f"{bench}@{proxy}", "-p 2222"], stderr=subprocess.STDOUT)
