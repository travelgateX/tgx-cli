import json
from six.moves import urllib


class GraphQLClient:
    """Class to use GraphQL on Python.

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
            raise e