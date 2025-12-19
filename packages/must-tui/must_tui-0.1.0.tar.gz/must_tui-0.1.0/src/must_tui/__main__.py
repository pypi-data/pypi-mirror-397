from pathlib import Path
import importlib

from .mib import read_pcf
from .must_app import MUSTApp
from .must import get_all_data_providers, login


def main():
    pcf_path = importlib.resources.files("must_tui").joinpath("data/mib/pcf.dat")
    # pcf_path = importlib.resources.path("must_tui", "data/mib/pcf.dat")
    pcf_content = read_pcf(pcf_path)

    ctx = login()
    _ = get_all_data_providers(ctx)

    MUSTApp(ctx, pcf_content).run()


if __name__ == "__main__":
    main()
