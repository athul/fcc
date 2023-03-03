import click
import requests

from fcc.utils.utils import generate_tokens,TOKEN_AUTH_HEADER

@click.command()
@click.option("--username",prompt="Frappe Cloud Username",help="Username for Frappe Cloud")
@click.option("--password",prompt="Frappe Cloud Password",hide_input=True)
def login(username,password):
    print(username, password)
    creds = {"usr":username,"pwd":password}
    session = requests.Session()
    login = session.post("http://135.181.42.205:8000/api/method/login",creds)
    if login.ok:
        click.secho("Authorization Successfull",fg="green")
        generate_tokens(session=session)


@click.command()
def getme():
    try:
        me = requests.get("http://135.181.42.205:8000/api/method/press.api.account.me",headers=TOKEN_AUTH_HEADER)
        if me.ok:
            click.secho(me.json(),fg="green")
    except:
        click.secho("Token Not found in fine", fg="red")


