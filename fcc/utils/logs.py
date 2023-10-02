import requests
import click
import time
from fcc.utils.utils import TOKEN_AUTH_HEADER


def get_logs_of_deploy(name: str):
    _log = []
    content_length = 0
    steps = 0
    last_step = []
    # breakpoint()
    while True:
        steps += 1
        res = requests.post(
            "https://frappecloud.com/api/method/press.api.bench.candidate",
            headers=TOKEN_AUTH_HEADER,
            data={"name": name},
        )
        if res.ok:
            logs = res.json()["message"]
            new_content_length = int(res.headers.get("content-length"))
            if logs["status"] == "Success" and steps > 1:
                click.secho("\n✅ Build Succeded\n", fg="bright_green")
                break
            if logs["status"] == "Failure":
                click.secho("❌ Deployment Failed", fg="red")
                break
            if logs["status"] != "Pending":
                if content_length == new_content_length and steps > 5:
                    break
                content_length = new_content_length
            build_steps = logs["build_steps"]
            if steps >= 1:
                s1 = set(map(lambda x: frozenset(x.items()), _log))
                s2 = set(map(lambda x: frozenset(x.items()), build_steps))
                new_diff = [dict(x) for x in s2 - s1]
                _log = new_diff
            else:
                _log = build_steps
            # print(_log)
            for log in _log:
                # if log["status"] != "Pending":
                build_stage = f'{log["stage"]} - {log["step"]}'
                # if build_stage in last_step:
                #     print("onnude", steps)
                #     break
                if steps % 5 == 0:
                    click.secho(f"\n🛠 {build_stage}", fg="bright_green")
                if log["cached"]:
                    click.secho(f"\n💲 {log['command']}\n", fg="magenta")
                    click.secho("\n⚡️ Cached\n", fg="cyan")
                else:
                    print("Ivde")
                    try:
                        click.secho(
                            f'\n💲 {log["command"] or ""}\n', fg="magenta")
                    except KeyError:
                        if steps < 3:
                            break
                        else:
                            pass
                    try:
                        click.secho(f'\n🖨 {log["output"]}\n', fg="yellow")
                    except:
                        pass
                last_step.append(build_stage)
                # print(last_step)
        else:
            print("Not Ok")
        time.sleep(3)


# if __name__ == "__main__":
#     name = input("Enter the name of the deployment: ")
#     get_logs_of_deploy(name)
