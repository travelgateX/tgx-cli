import json
from six.moves import urllib
import configuration

MODE = configuration.MODE
GRAPH_URL = configuration.GRAPH_URL
USER_TOKEN = configuration.USER_TOKEN


class GraphQLClient:
    """Class to manage GraphQL
    """

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
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers['Authorization'] = '{}'.format(self.token)

        req = urllib.request.Request(
            self.endpoint, json.dumps(data).encode('utf-8'), headers)

        try:
            response = urllib.request.urlopen(req)
            response_json = json.loads(response.read().decode('utf-8'))
            return response_json
        except urllib.error.HTTPError as e:
            print((e.read()))
            print('')
            raise e


def create_organization(owner, code):
    """Function to create an organization.

    :param owner: email address of the organization owner
    :param code: code to be used by the organization
    :return: JSON with the Graph QL response

    """
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    mutation = """mutation{
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
                }""".replace('USER_TEMPLATE', owner).replace(
                'CODE_TEMPLATE', code)

    print("\n\n==============================\n")
    print("1st step) Creating Organization... \t user: {} \t code: {}".format(
        owner, code))
    result = client.execute(mutation)
    print(result)
    error = result['data']['admin']['createOrganization']['error']
    if error is not None:
        first_error = result['data']['admin']['createOrganization']['error'][0]
        error_description = first_error['description']
        print("\n")
        print(error_description)
    return result


def get_hotel(code):
    """ Function to get an Hotel by the organization code.

    :param code: Organization code
    :return: String with the Hotel code or error
    """
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    query = """{
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
        }""".replace('CODE_TPL', code)
    print("\n==============================\n")
    print("2nd step) Getting HotelX... \t code: {}".format(code))
    result = client.execute(query)
    print(result)

    try:
        edges = result['data']['admin']['organizations']['edges'][0]['node'][
            'organizationData']['children']['edges'][0]['node']['groupData'][
            'children']['edges']
        for edge in edges:
            code = edge['node']['groupData']['code']
            if code.startswith('HotelX_'):
                print("\nGroup: {}".format(code))
                return code
    except KeyError:
        print("\n****************")
        print("**** ERROR *****")
        print("****************")
        print("An error occurred while creating organization.")
        print()
        return "Error "


def update_group(api, code):
    """ Function to update the group on an API

    :param api: API code
    :param code: HotelX code
    :return: JSON with the API result
    """
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    mutation = """mutation{
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
                }""".replace('API_TEMPLATE', api).replace('CODE_TEMPLATE', code)

    print("\n------------------------------\n")
    print("3rd step) Updating Group...\t api: {} \t code: {} ".format(
    api, code))
    result = client.execute(mutation)
    print(result)
    return result


def create_member(code):
    """ Function to add a member to a group and creates the API key

    :param code: Group code
    :return: API Key or error
    """
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    # PROD
    if MODE == 'PROD':
        mutation = """mutation{
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
                    }""".replace('CODE_TEMPLATE', code)

    # TEST
    else:
        mutation = """mutation{
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
                    }""".replace('CODE_TEMPLATE', code)

    print("\n==============================\n")
    print("4th step) Creating member... \t code: {}".format(code))
    result = client.execute(mutation)
    print(result)
    try:
        api_key = result['data']['admin']['createMember']['code']
        print("\nApiKey: {}".format(api_key))
        return api_key
    except KeyError:
        print("\n****************")
        print("**** ERROR *****")
        print("****************")
        print("An error occurred on creating member with Keys")
        try:
            error = result['data']['admin']['createMember']['error'][0]
            error_description = error['description']
        except KeyError:
            error_description = 'Unknown key'
        except TypeError:
            error_description = 'Unknown type'
        return "Error: " + error_description
    except TypeError:
        print("\n****************")
        print("**** ERROR *****")
        print("****************")
        print("An error occurred on creating member with Types")
        try:
            error = result['data']['admin']['createMember']['error'][0]
            error_description = error['description']
        except KeyError:
            error_description = 'Unknown key'
        except TypeError:
            error_description = 'Unknown type'
        return "Error: " + error_description


def update_member(code, group, role_resource_tuple):
    """ Updates the member Group or role resource

    :param code: Member code
    :param group: Group of the member
    :param role_resource_tuple: Tuple of role and resource
    :return: API result as json or error
    """
    client = GraphQLClient(GRAPH_URL)
    client.inject_token(USER_TOKEN)
    mutation = """mutation{
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
                }""".replace('CODE_TEMPLATE', code).replace(
                'GROUP_TEMPLATE', group)
    mutation = mutation.replace('ROLE_TEMPLATE', role_resource_tuple[0])
    mutation = mutation.replace('RESOURCE_TEMPLATE', role_resource_tuple[1])
    result = client.execute(mutation)
    print('\n-------------------------------------------------------\n')
    print("5th step) Updating Member ...")
    print(result)
    # print("code: "+code)
    print("\ngroup: " + group)
    print("role: " + role_resource_tuple[0])
    print("resource: " + role_resource_tuple[1])
    print("ApiKey: " + result['data']['admin']['updateMember']['code'])
    print('\n-------------------------------------------------------')
    try:
        response = result['data']['admin']['updateMember']['code']
    except KeyError:
        response = "Error on key response from API "
        print(response)
    except TypeError:
        response = "Error on type response from API "
        print(response)
    return response


role_resource_list_prod = [('viewer', 'mbr'),
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

role_resource_list_dev = [('owner', 'mbr')]


def init_create_all(init_owner, init_code):
    """Function to create all the permissions on an owner on a new organization.

    :param init_owner: Email of the owner
    :param init_code: Code of the organization
    :return: void or -1 only on case of error
    """
    code2 = init_create_organization(init_owner, init_code)
    if code2 == -1:
        return -1

    apikey = init_create_apikey(code2)
    if apikey == -1:
        return -1


def init_create_organization(init_owner, init_code):
    """ Function to coordinate the organization creation

    :param init_owner: email of the owner of the organization
    :param init_code: code of the organization
    :return: org code or -1 only on case of error
    """
    create_organization(init_owner, init_code)
    code2 = get_hotel(init_code)
    if code2.startswith("Error"):
        print("\n" + code2)
        return -1
    for api in ["entity", "hubgra", "hotlst"]:
        update_group(api, code2)
    return code2


def init_create_apikey(group_code):
    """ Function to create the apikey of a group and grant permissions

    :param group_code: group code
    :return:
    """
    code4 = create_member(group_code)
    if code4.startswith("Error"):
        print("\n" + code4)
        return -1

    if MODE == 'PROD':
        for role_resource in role_resource_list_prod:
            update_member(code4, group_code, role_resource)
    else:  # MODE == TEST
        for role_resource in role_resource_list_dev:
            return update_member(code4, group_code, role_resource)
