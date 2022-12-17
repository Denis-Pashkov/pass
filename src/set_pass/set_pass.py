# PASS package
# (c) kol, 2022
# MIT licence

import keyring
import json
import click
from getpass import getpass, getuser
from collections import defaultdict
from typing import Mapping, Tuple

from keyring.backends import Windows
keyring.set_keyring(Windows.WinVaultKeyring())

class PasswordStore:
    META_KEY = 'kol.pass.__meta__'
    PASS_KEY = 'kol.pass.{service}'
    DEFAULT_SERVICES = {
        'version': '1.0',
        'services': defaultdict(list)
    }

    def __init__(self):
        self.user: str = getuser()
        self.__meta: dict = None

    @property
    def meta(self) -> Mapping:
        if self.__meta is None:
            meta = keyring.get_password(self.META_KEY, self.user)
            if meta is None:
                self.__meta = self.DEFAULT_SERVICES
            else:
                self.__meta = json.loads(meta)
                if 'version' not in self.__meta:
                    self.__meta['version'] = self.DEFAULT_SERVICES['version']
                if 'services' not in self.__meta:
                    self.__meta['services'] = defaultdict(list)
                else:
                    self.__meta['services'] = defaultdict(list, self.__meta['services'])
        return self.__meta

    @property
    def services(self) -> Mapping:
        return self.meta['services']

    def default_login(self, service: str) -> str:
        return self.user if not len(self.services.get(service, [])) \
            else self.services[service][0]

    def save(self):
        keyring.set_password(self.META_KEY, self.user, json.dumps(self.meta))

    def rebuild(self):
        pass

    def import_file(self, file: click.File):
        d = json.loads(file.read())
        if not d:
            print('ERROR: File seems empty, import cancelled')
            return

    def export(self, file: click.File):
        if not self.services:
            print('ERROR: No service logins found, export cancelled')
            return

        d = {srv: {login: self.get_pass(srv, login) for login in logins} \
            for srv, logins in self.services.items()}
        file.write(json.dumps(d, indent=4, ensure_ascii=False))

    def print_service_logins(self):
        if not self.services:
            print('No service logins found')
        else:
            print('\n'.join([f'{srv}: {logins}' for srv, logins in self.services.items()]))

    def add_service_login(self, service: str, login: str):
        if service not in self.meta['services'] or login not in self.meta['services'][service]:
            self.meta['services'][service].append(login)
        self.save()

    def remove_service_login(self, service: str, login: str):
        if service in self.meta['services'] and login in self.meta['services'][service]:
            self.meta['services'][service] = [x for x in self.meta['services'][service] if x != login]
        self.save()

    def get_pass(self, service: str, login: str = None) -> str:
        return self.get_login_pass(service, login)[1]

    def get_login_pass(self, service: str, login: str = None) -> Tuple[str, str]:
        if not login: 
            login = self.default_login(service)
        return login, keyring.get_password(self.PASS_KEY.format(service=service), login)

    def set_pass(self, service: str, login: str = None, passwd: str = None) -> None:
        login = login or self.user
        if passwd is None:
            while True:
                passwd = getpass(f'Enter password for user {login}@{service}:')
                passwd2 = getpass('Repeat for confirmation:')
                if passwd == passwd2:
                    break
                else:
                    print('Passwords do not match')

        keyring.set_password(self.PASS_KEY.format(service=service), login, passwd)
        self.add_service_login(service, login)
        return passwd

    def remove_pass(self, service: str, login: str = None) -> None:
        login = login or self.user
        keyring.delete_password(self.PASS_KEY.format(service=service), login)
        store.remove_service_login(service, login)

store = PasswordStore()

@click.command(no_args_is_help=True)
@click.option('-l', '--list', is_flag=True, help='List services and logins')
@click.option('-a', '--add', help='Add service login. Use -u and -p to specify login and password')
@click.option('-u', '--login', help='Login to store')
@click.option('-p', '--password', help='Password to store')
@click.option('-s', '--show', help='Show password fo service login. Use -u to specify login')
@click.option('-d', '--delete', help='Remove service login. Use -u to specify login')
@click.option('--sync', 
    help='Resync metadata and actual keystore (not implemented yet)')
@click.option('--import', 'import_file', type=click.File('rt', lazy=True), 
    help='Import service logins from file (not implemented yet)')
@click.option('--export', type=click.File('wt', lazy=True), help='Export service logins to file')
def main(list, add, show, delete, sync, import_file, export, login, password):
    if list:
        print('List of login and services stored in the system keyring:\n---')
        store.print_service_logins()
        print('---')
    elif add:
        store.set_pass(add, login=login, passwd=password)
        print('Service login added')
    elif show:
        login, passwd = store.get_login_pass(show, login=login)
        if not passwd:
            print(f'Password for {login}@{show} is empty or not set')
        else:
            print(f'Password for {login}@{show} is {passwd}')
    elif delete:
        store.remove_pass(delete, login)
        print('Service login removed')
    elif sync:
        store.rebuild()
    elif import_file:
        store.import_file(import_file)
    elif export:
        store.export(export)

if __name__ == '__main__':
    main()
