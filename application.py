"""
main application page
"""
import os

import requests

CONFIG_NAME = os.getenv('FLASK_CONFIG')

APP = os.name(CONFIG_NAME)
APPLOATION = 'run'
CONFIG_NAME = 'run.py'
CLIENT_ID = '702558371020-uuj5jmirch3lb3nhne0vandic6sal544.apps.googleusercontent.com'
CLIENT_PASSWORD = 'Yi-5tWIvE9mxsS93ial8QKrX'
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

'''
function to pront provider
'''
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

APP.run(ssl_context="adhoc")

if __name__ == '__main__':
    APP.run(debug=True)
