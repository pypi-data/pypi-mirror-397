from .fabi_demo import DEMO as DEMO
from _typeshed import Incomplete
from rich.progress import BarColumn as BarColumn, Progress as Progress, SpinnerColumn as SpinnerColumn, TextColumn as TextColumn, TimeRemainingColumn as TimeRemainingColumn
from time import sleep as sleep

class Config:
    def __init__(self) -> None: ...

pass_config: Incomplete
console: Incomplete

@pass_config
def cli(config) -> None: ...
@pass_config
def reescale(config: Config, input_dir): ...
