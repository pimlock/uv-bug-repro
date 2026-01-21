import typer

app = typer.Typer()

@app.command()
def hello():
    print("Hello from repro-cli!")

def main():
    app()
