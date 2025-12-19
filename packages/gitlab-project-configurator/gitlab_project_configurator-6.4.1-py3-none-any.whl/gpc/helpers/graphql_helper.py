# Standard Library
from typing import Dict  # noqa: F401

# Gitlab-Project-Configurator Modules
from gpc.helpers.exceptions import GpcError
from gpc.helpers.session_helper import create_retry_request_session


class Singleton(type):
    _instances = {}  # type: Dict[type, type]

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class GraphqlSession:
    def __init__(self, gitlab_url, gitlab_token):
        self._gql_url = f"{gitlab_url.rstrip('/')}/api/graphql"
        self._gitlab_token = gitlab_token
        self.session = create_retry_request_session()
        self.session.headers.update({"Authorization": "Bearer " + self._gitlab_token})

    def run_graphql_query(self, query):
        request = self.session.post(
            self._gql_url,
            json={"query": query},
        )
        if request.status_code == 200:
            return request.json()

        raise GpcError(f"Unexpected status code returned: {request.status_code}")


class GraphqlSingleton(GraphqlSession, metaclass=Singleton):
    pass
