import argparse
import sys
import tgx


class ClientParser(object):
    """ Class to parse the main file.

        Parse_args defaults to [1:] for args, but you need to exclude the rest of the args too, or validation will fail
    """
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Tool that you can use to manage your TravelgateX platform',
            usage='''tgx COMMAND
            Options:
                --endpoint              Gateway endpoint.
                --auth_type             ak or apikey, br or bearer
                --auth_type             Auth Token

            Commands:
                organization            Create organization or an organization with apikey
                apikey                  Create apikey
                configure               Configure the access data   

            --
            ''')
        parser.add_argument('command', help='Choose a Command to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def organization(self):
        def create_all():
            tgx.init_create_all(args.user, args.organization_code)

        def create():
            tgx.init_create_organization(args.user, args.organization_code)

        parser = argparse.ArgumentParser(description='Create Organization and Apikey or only Organization')
        subparsers = parser.add_subparsers(dest='command2')
        subparser_create_all = subparsers.add_parser('create_all', help=create_all.__doc__)
        subparser_create_all.add_argument('--user', default=None)
        subparser_create_all.add_argument('--organization_code', default=None)
        subparser_create = subparsers.add_parser('create', help=create.__doc__)
        subparser_create.add_argument('--user', default=None)
        subparser_create.add_argument('--organization_code', default=None)
        args = parser.parse_args(sys.argv[2:])
        if args.command2 == 'create':
            # print("if args.command2=='create':")
            create()
        elif args.command2 == 'create_all':
            # print("elif args.command2=='create_all':")
            create_all()
        else:
            print("Invalid command")

    def configure(self):
        parser = argparse.ArgumentParser(description='Configure access to GraphQL')
        parser.add_argument("--mode", default='TEST')
        parser.add_argument("--endpoint")
        parser.add_argument("--auth")
        parser.add_argument("--auth_type")
        args = parser.parse_args(sys.argv[2:])
        user_token = args.auth
        if args.auth_type in ['ak', 'apikey']:
            user_token = 'Apikey ' + user_token
        if args.auth_type in ['br', 'bearer']:
            user_token = 'Bearer ' + user_token
        with open("configuration.py", "w") as file:
            file.write("# FILE AUTO-GENERATED BETTER DO NO EDIT PLEASE \n")
            file.write("MODE = '" + args.mode + "'\n")
            file.write("GRAPH_URL = '" + args.endpoint + "'\n")
            file.write("USER_TOKEN = '" + user_token + "'\n")

    def apikey(self):
        def create():
            tgx.init_create_apikey(args.group_user)
        parser = argparse.ArgumentParser(
            description='Create Apikey')
        subparsers = parser.add_subparsers(dest='command2')
        subparser_create = subparsers.add_parser('create', help=create.__doc__)
        subparser_create.add_argument('--group_user', default=None)
        subparser_create.add_argument('--endpoint', default=None)
        subparser_create.add_argument('--auth', default=None)
        subparser_create.add_argument('--auth_type', default='ak')  # Bearer
        args = parser.parse_args(sys.argv[2:])
        if args.command2 == 'create':
            create()
        else:
            print("Invalid command")


""" Example uses:
python main.py organization create_all --user aselma@xmltravelgate.com --organization_code TST221
python main.py configure --mode TEST --endpoint https:// --auth_type br --auth useyourown
"""


def main():
    pass


if __name__ == '__main__' or __name__ == 'tgx.main':
    ClientParser()
