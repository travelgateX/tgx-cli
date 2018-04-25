import json
from six.moves import urllib
# import requests
import argparse
import sys

# MODE='TEST'
MODE='PROD'

class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.token = None

    def execute(self, query, variables=None):
        return self._send(query, variables)



    def inject_token(self, token):
        self.token = token

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        # print(json.dumps(data).encode('utf-8').decode('ascii'))
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers['Authorization'] = '{}'.format(self.token)

        # print(headers)

        req = urllib.request.Request(self.endpoint, json.dumps(data).encode('utf-8'), headers)

        try:
            response = urllib.request.urlopen(req)
            response_json=json.loads(response.read().decode('utf-8'))
            return response_json
            # return response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e


def X1_createOrganization(user,code):
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    mutation="""mutation{
                    admin{
                        createOrganization(organization:{
                        user:"USER_TEMPLATE"
                        code:"CODE_TEMPLATE"
                        template:ORGANIZATION_DEFAULT
                        }){
                        error{
                            code
                            type
                            description
                        }
                        }
                    }
                }""".replace('USER_TEMPLATE',user).replace('CODE_TEMPLATE',code)

    result = client.execute(mutation)
    return result


def X2_get_HotelX(code):
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    query="""{
            admin {
                organizations(codes: "CODE_TPL") {
                edges {
                    node {
                    organizationData {
                        children {
                        edges {
                            node {
                            groupData {
                                children {
                                edges {
                                    node {
                                    groupData {
                                        code
                                    }
                                    }
                                }
                                }
                            }
                            }
                        }
                        }
                    }
                    }
                }
                }
            }
        }""".replace('CODE_TPL',code)

    result = client.execute(query)
    print(result)
    edges=result['data']['admin']['organizations']['edges'][0]['node']['organizationData']['children']['edges'][0]['node']['groupData']['children']['edges']
    for edge in edges:
        code=edge['node']['groupData']['code']
        if code.startswith('HotelX_'):
            return code
    return Exception



def X3_updateGroup(api,code):
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    mutation="""mutation{
                    admin{
                        updateGroup(
                            group:{
                                api:"API_TEMPLATE"
                                code:"CODE_TEMPLATE"
                                method:ADD
                                }
                                )
                                {
                                    error{
                                        code
                                        type
                                        description
                                        }
                                }
                        }
                }""".replace('API_TEMPLATE',api).replace('CODE_TEMPLATE',code)

    result = client.execute(mutation)
    return result

def X4_createMember(code):
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    #PROD
    if MODE=='PROD':
        mutation="""mutation{
                        admin{
                            createMember(member:{
                            type:SERVICE_ACCOUNT
                            group:"CODE_TEMPLATE"
                            roles:"viewer"
                            resource:"grp"
                            }){
                            error{
                                code
                                type
                                description
                            }
                            }
                        }
                    }""".replace('CODE_TEMPLATE',code)

    # TEST
    if MODE=='TEST':
        mutation="""mutation{
                        admin{
                            createMember(member:{
                            type:SERVICE_ACCOUNT
                            group:"CODE_TEMPLATE"
                            roles:"owner"
                            resource:"grp"
                            }){
                                code
                            error{
                                code
                                type
                                description
                            }
                            }
                        }
                    }""".replace('CODE_TEMPLATE',code)

    result = client.execute(mutation)
    return result['data']['admin']['createMember']['code']


def X5_updateMember(code,group,role_resource_tuple):
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    mutation="""mutation{
                    admin{
                        updateMember(member:{
                        code:"CODE_TEMPLATE"
                        group:"GROUP_TEMPLATE"
                        roles:"ROLE_TEMPLATE"
                        resource:"RESOURCE_TEMPLATE"
                        method:ADD
                        }){
                            code
                        error{
                            code
                            type
                            description
                        }
                        }
                    }
                }""".replace('CODE_TEMPLATE',code).replace('GROUP_TEMPLATE',group)
    mutation=mutation.replace('ROLE_TEMPLATE',role_resource_tuple[0])
    mutation=mutation.replace('RESOURCE_TEMPLATE',role_resource_tuple[1])
    result = client.execute(mutation)
    print('\n===========================================================')
    # print("code: "+code)
    print("group: "+group)
    print("role: "+role_resource_tuple[0])
    print("resource: "+role_resource_tuple[1])
    print("ApiKey: " + result['data']['admin']['updateMember']['code'])
    print('===========================================================\n')
    return result['data']['admin']['updateMember']['code']
    # return result

role_resource_list_prod=[('viewer', 'mbr'),
 ('viewer', 'prd'),
 ('viewer', 'api'),
 ('viewer', 'rsc'),
 ('viewer', 'rol'),
 ('viewer', 'acc'),
 ('viewer', 'sup'),
 ('viewer', 'cli'),
 ('exec', 'src'),
 ('exec', 'qte'),
 ('exec', 'boo'),
 ('exec', 'bok'),
 ('exec', 'cnl'),
 ('exec', 'brd'),
 ('exec', 'cat'),
 ('exec', 'rom'),
 ('exec', 'hot')]

role_resource_list_dev=[('owner', 'mbr')]


def X_create_all(init_user,init_code):
    X1_createOrganization(init_user,init_code)

    code2=X2_get_HotelX(init_code)
    print("\n\n===========================\nGroup: " + code2)


    for api in ["entity", "hubgra", "hotlst"]:
        X3_updateGroup(api,code2)

    code4=X4_createMember(code2)

    if MODE=='TEST':
        for role_resource in role_resource_list_dev:
            X5_updateMember(code4,code2,role_resource)
    if MODE=='PROD':
        for role_resource in role_resource_list_prod:
            X5_updateMember(code4,code2,role_resource)


def X_create_organization(init_user,init_code):
    X1_createOrganization(init_user,init_code)

    code2=X2_get_HotelX(init_code)
    print("Group: " + code2)


    for api in ["entity", "hubgra", "hotlst"]:
        X3_updateGroup(api,code2)

def X_create_apikey(group_code):
    code4=X4_createMember(group_code)

    if MODE=='TEST':
        for role_resource in role_resource_list_dev:
            return X5_updateMember(code4,group_code,role_resource)
    if MODE=='PROD':
        for role_resource in role_resource_list_prod:
            X5_updateMember(code4,group_code,role_resource)





class cli(object):
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

            --
            ''')
        parser.add_argument('command', help='Subcommand to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print ('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def globalize_args(self,args):
        global GRAPH_URL
        global USER_TOKEN
        GRAPH_URL = args.endpoint
        USER_TOKEN = args.auth

        if args.auth_type in ['ak','apikey']:
            USER_TOKEN = 'Apikey ' + USER_TOKEN
        if args.auth_type in ['br','bearer']:
            USER_TOKEN = 'Bearer ' + USER_TOKEN

        # print(USER_TOKEN)
        # print(GRAPH_URL)

    def organization(self):
        def create_all():
            # print("def create_all():")
            X_create_all(args.user,args.organization_code)
        def create():
            # print("def create():")
            X_create_organization(args.user,args.organization_code)
        parser = argparse.ArgumentParser(
            description='Create Organization and Apikey or only Organization')
        subparsers = parser.add_subparsers(dest='command2')

        subparser_create_all = subparsers.add_parser('create_all', help=create_all.__doc__)#organization create_all [CODDE]
        subparser_create_all.add_argument('--user', default=None)
        subparser_create_all.add_argument('--organization_code', default=None)#organization create [CODDE]
        subparser_create_all.add_argument('--endpoint', default=None)
        subparser_create_all.add_argument('--auth', default=None)
        subparser_create_all.add_argument('--auth_type', default='ak')# Bearer

        subparser_create = subparsers.add_parser('create', help=create.__doc__)
        subparser_create.add_argument('--user', default=None)
        subparser_create.add_argument('--organization_code', default=None)
        subparser_create.add_argument('--endpoint', default=None)
        subparser_create.add_argument('--auth', default=None)
        subparser_create.add_argument('--auth_type', default='ak')# Bearer

        args = parser.parse_args(sys.argv[2:])

        self.globalize_args(args)

        if args.command2=='create':
            # print("if args.command2=='create':")
            create()
        elif args.command2=='create_all':
            # print("elif args.command2=='create_all':")
            create_all()
        else:
            print("Invalid command")

    def apikey(self):
        def create():
            X_create_apikey(args.group_user)

        parser = argparse.ArgumentParser(
            description='Create Apikey')

        subparsers = parser.add_subparsers(dest='command2')

        subparser_create = subparsers.add_parser('create', help=create.__doc__)
        subparser_create.add_argument('--group_user', default=None)
        subparser_create.add_argument('--endpoint', default=None)
        subparser_create.add_argument('--auth', default=None)
        subparser_create.add_argument('--auth_type', default='ak')# Bearer

        args = parser.parse_args(sys.argv[2:])

        self.globalize_args(args)

        if args.command2=='create':
            create()
        else:
            print("Invalid command")

def main():
    pass

if __name__ == "tgx.tgx":
# if __name__ == '__main__':
    cli()
