from __future__ import print_function
import os

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import argparse
from PeerReview.settings import SCOPES

CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Classroom API Python Quickstart'
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


def get_credentials():
    """
    OAuth2 flow is completed to obtain  and store the new credentials.
    Returns: None
    """
    home_dir = os.getcwd()
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'classroom.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=SCOPES)
    flow.params['access_type'] = 'offline'  # offline access
    flow.params['include_granted_scopes'] = 'true'  # incremental auth
    flow.user_agent = APPLICATION_NAME
    tools.run_flow(flow, store, flags)


if __name__ == '__main__':
    get_credentials()
