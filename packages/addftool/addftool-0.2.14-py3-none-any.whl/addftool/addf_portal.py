import argparse
from addftool.process import add_killer_args, killer_main
from addftool.sync import add_sync_args, sync_main
from addftool.deploy import add_deploy_args, deploy_main
from addftool.broadcast_folder import add_broadcast_folder_args, broadcast_folder_main
from addftool.sleep import add_sleep_args, sleep_main

from addftool.blob import add_blob_args, blob_main

# Import version information
try:
    from importlib.metadata import version
    __version__ = version("addftool")
except ImportError:
    # Fallback for older Python versions
    import pkg_resources
    __version__ = pkg_resources.get_distribution("addftool").version
except:
    # Fallback if package is not installed
    __version__ = "0.2.11"  # Keep in sync with pyproject.toml


def get_args():
    parser = argparse.ArgumentParser(description="Addf's tool")
    
    # Add version argument
    parser.add_argument(
        '--version', '-v', 
        action='version', 
        version=f'addftool {__version__}'
    )

    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')
    add_killer_args(subparsers)
    add_sync_args(subparsers)
    add_deploy_args(subparsers)
    add_broadcast_folder_args(subparsers)
    add_blob_args(subparsers)
    add_sleep_args(subparsers)

    return parser.parse_args()


def main():
    args = get_args()
    if args.command == "kill":
        killer_main(args)
    elif args.command == "sync":
        sync_main(args)
    elif args.command == "deploy":
        deploy_main(args)
    elif args.command == "broadcast-folder":
        broadcast_folder_main(args)
    elif args.command == "blob":
        blob_main(args)
    elif args.command == "sleep":
        sleep_main(args)
    else:
        print("Unknown command: ", args.command)


if __name__ == "__main__":
    main()
