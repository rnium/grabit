import typer
from getpass import getpass
import uvicorn
from .validators import minlen
from app.config.database import SessionLocal
from app.crud.users import create_user

app = typer.Typer()


@app.command()
def createuser():
    name = typer.prompt('Your name', value_proc=minlen)
    username = typer.prompt('Username', value_proc=minlen)
    password = getpass('Password: ')
    re_password = getpass('Retype password: ')
    
    while password != re_password:
        re_password = getpass('Mismatch, retype password again: ')
    with SessionLocal() as db:
        try:
            create_user(db, {'username': username, 'name': name, 'password': password})
        except Exception as e:
            typer.echo('Error: {}'.format(e))
            raise typer.Exit(1)
    typer.echo('User created')

    
@app.command()
def runserver(
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = True
    ):
    uvicorn.run('app.main:app', host=host, port=port, reload=reload)


