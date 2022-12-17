# PASS Python package

This small package allows to store passwords in the system keyring protected storage
so they would be secured and easily available at the same time.

## Installation

Build the module and install it with `pip`. Run at package root directory:

    pip install build
    python -m build .
    pip install dist\pass-1.0.0-py3-none-any.whl

## Usage

To use simply run `pass` command from command prompt. The following options are available:

    -l, --list           List services and logins
    -a, --add TEXT       Add service login. Use -u and -p or -g to specify login and
                        password
    -u, --login TEXT     Login to store
    -p, --password TEXT  Password to store
    -g                   Generate strong password (will print it out)
    -s, --show TEXT      Show password fo service login. Use -u to specify login
    -d, --delete TEXT    Remove service login. Use -u to specify login
    --sync TEXT          Resync metadata and actual keystore
    --export TEXT        Export metadata to file
    --help               Show help message and exit.

Add new service login to keyring:

    pass -a <service> -u <user> [-p <password>, -g]

Show service password:

    pass -s <service> [-u <user>]
