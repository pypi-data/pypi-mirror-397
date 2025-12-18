import typer

from mtmai.core import bootstrap_core

bootstrap_core()
app = typer.Typer(invoke_without_command=True)
