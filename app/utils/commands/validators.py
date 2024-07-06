import typer

def minlen(val):
    if len(val) < 4:
        raise typer.BadParameter('must be at least 4 characters long')
    return val