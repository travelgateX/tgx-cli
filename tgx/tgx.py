import json
from six.moves import urllib
# import requests
import argparse
try:
    import Bearer
except:
    print("\n\n======================================")
    print("Please config your token to access.")
    print("In order to do that you can type:")
    print("python tgx.py config -token eyJ0eXAiOiJKV1QiL....")
    print("In that point it is needed to substitute eyJ0eXAiOiJKV1QiL.... with your organization token")
    print("This will create a Bearer.py file containing token=YOUR_TOKEN")
    print("There is no problem in changing this token manually directly in the file Bearer.py")
    print("=========================================================================================\n\n")


MODE=os.environ['CLI_MODE']


if MODE=='TEST':
    GRAPH_URL   = os.environ['GRAPH_URL_DEV']  # SIMPLE API ENDPOINT    
    
if MODE=='PROD':
    GRAPH_URL   = os.environ['GRAPH_URL_PROD']
    
try:
    USER_TOKEN = 'Bearer ' + Bearer.token
except:
    pass

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
    print("code: "+code)
    print("group: "+group)
    print("roles: "+role_resource_tuple[0])
    print("resource: "+role_resource_tuple[1])
    print(result['data']['admin']['updateMember']['code'])
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


def create_all(init_user,init_code):
    X1_createOrganization(init_user,init_code)

    code2=X2_get_HotelX(init_code)
    print("Group: " + code2)
    

    for api in ["entity", "hubgra", "hotlst"]:
        X3_updateGroup(api,code2)

    code4=X4_createMember(code2)

    if MODE=='TEST':
        for role_resource in role_resource_list_dev:
            X5_updateMember(code4,code2,role_resource)
    if MODE=='PROD':
        for role_resource in role_resource_list_prod:
            X5_updateMember(code4,code2,role_resource)


def create_organization(init_user,init_code):
    X1_createOrganization(init_user,init_code)

    code2=X2_get_HotelX(init_code)
    print("Group: " + code2)
    

    for api in ["entity", "hubgra", "hotlst"]:
        X3_updateGroup(api,code2)

def create_apikey(group_code):
    code4=X4_createMember(group_code)

    if MODE=='TEST':
        for role_resource in role_resource_list_dev:
            return X5_updateMember(code4,group_code,role_resource)
    if MODE=='PROD':
        for role_resource in role_resource_list_prod:
            X5_updateMember(code4,group_code,role_resource)


def config(token):
    print("Configurando Bearer...")
    with open("./Bearer.py","w") as bearer_file:
        bearer_file.write('token="' + token + '"')
    print("Configurado Bearer")

def get_token():
    import login
    login.main()

def main():
    pass


if __name__ == "tgx.tgx":
# if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(dest='command')


    subparser_create_all = subparsers.add_parser('create_all', help=create_all.__doc__)
    subparser_create_all.add_argument('-user', default=None)
    subparser_create_all.add_argument('-organization_code', default=None)

    subparser_create_organization = subparsers.add_parser('create_organization', help=create_organization.__doc__)
    subparser_create_organization.add_argument('-user', default=None)
    subparser_create_organization.add_argument('-organization_code', default=None)

    subparser_create_apike = subparsers.add_parser('create_apikey', help=create_organization.__doc__)
    subparser_create_apike.add_argument('-group_user', default=None)
    
    subparser_config=subparsers.add_parser('config', help=config.__doc__)
    subparser_config.add_argument('-token', default=None)

    subparser_get_token=subparsers.add_parser('get_token', help=config.__doc__)

    args = parser.parse_args()

    if args.command == 'create_all':
        create_all(args.user,args.organization_code)

    elif args.command == 'create_organization':
        create_organization(args.user,args.organization_code)

    elif args.command == 'create_apikey':
        create_apikey(args.group_user)

    elif args.command == 'config':
        config(args.token)

    elif args.command == 'get_token':
        get_token()

    else:
        print("\nNot operation specified")
        print("\nPossible options are:")
        print("=======================")
        print("python tgx.py config \t-token YOUR_TOKEN")
        print("\npython tgx.py create_all \t\t-user YOUR_USER \t-organization_code YOUR_ORGANIZATION_CODE")
        print("python tgx.py create_organization \t-user YOUR_USER \t-organization_code YOUR_ORGANIZATION_CODE")
        print("python tgx.py create_apikey \t-group_user YOUR_GROUP_USER")
        print("\npython tgx.py get_token")


    

    
    
