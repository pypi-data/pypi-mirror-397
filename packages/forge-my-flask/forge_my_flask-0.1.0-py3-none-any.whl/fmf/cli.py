from fmf.processes.api import init_api_project
from fmf.processes.webapp import init_webapp_project
from fmf.utils.version import __version__ as fmf_version
import argparse


def print_banner():
    print(r"""  
 ____  _____  ____   ___  ____    __  __  _  _    ____  __      __    ___  _  _ 
( ___)(  _  )(  _ \ / __)( ___)  (  \/  )( \/ )  ( ___)(  )    /__\  / __)( )/ )
 )__)  )(_)(  )   /( (_-. )__)    )    (  \  /    )__)  )(__  /(__)\ \__ \ )  ( 
(__)  (_____)(_)\_) \___/(____)  (_/\/\_) (__)   (__)  (____)(__)(__)(___/(_)\_)
          
          Forge My Flask (FMF)
""")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="fmf",
        description="Forge My Flask - Flask project scaffolder"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {fmf_version}"
    )

    return parser.parse_args()


def init_menu():
    print_banner()
    print("1. API Project")
    print("2. WebApp Project")

    choice = input("Select an option (1-2): ")

    if choice == "1":
        init_api_project()
    elif choice == "2":
        init_webapp_project()


def main():
    parse_args()
    init_menu()
