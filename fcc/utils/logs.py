import requests
import click
import time
from fcc.utils.utils import TOKEN_AUTH_HEADER


def get_logs_of_deploy(name: str):
    _logs = {}
    content_length = 0
    while True:
        res = requests.post(
            "http://fc:8000/api/method/press.api.bench.candidate",
            headers=TOKEN_AUTH_HEADER,
            data={"name": name},
        )
        if res.ok:
            logs = res.json()["message"]
            new_content_length = int(res.headers.get("content-length"))
            if logs["status"] == "Success":
                click.secho("\nBuild Succeded\n", fg="green")
                break
            if logs["status"] == "Failure":
                click.secho("Deployment Failed", fg="red")
                break
            if logs["status"] != "Pending":
                if content_length == new_content_length:
                    break
                content_length = new_content_length
            _logs.update(logs)
            for log in _logs["build_steps"]:
                if log["status"] != "Pending":
                    click.secho(
                        f'\n{log["stage"]} - {log["step"]}', fg="green")
                    if log["cached"]:
                        click.secho("\nCached\n", fg="cyan")
                        click.secho(f"\n{log['command']}\n", fg="cyan")
                    else:
                        try:
                            click.secho(f'\n{log["command"]}\n', fg="cyan")
                        except:
                            pass
                        click.secho(f'\n{log["output"]}\n', fg="yellow")
        time.sleep(2)
