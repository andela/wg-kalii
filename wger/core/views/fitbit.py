import requests
import urllib
import base64
import os

class FitBit:
    """Class to handle all fitbit operation"""
    # App settings from fitbit as regards the app
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    SCOPE = os.getenv('SCOPE')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    # Authorization and authentication URIs
    AUTHORIZE_URI = os.getenv('AUTHORIZE_URI')
    TOKEN_REQUEST_URI = os.getenv("TOKEN_REQUEST_URI")
    
    def ComposeAuthorizationuri(self):
        """Creates a unique  url for authorization for each user
        """
        # parameters for authorization
        params = {
            'client_id': self.CLIENT_ID,
            'response_type': 'code',
            'scope': self.SCOPE,
            'redirect_uri': self.REDIRECT_URI
        }
        # encode the parameters
        urlparams = urllib.parse.urlencode(params)
        # construct and return authorization_uri
        return self.AUTHORIZE_URI + '?' + urlparams


    def RequestAccessToken(self, code):
        """Generates url for fit bit authorization """
        # Authentication header
        client_id = self.CLIENT_ID.encode('utf-8')
        headers = {
            'Authorization': os.environ.get('Authorization'),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # parameters for requesting tokens
        params = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'redirect_uri': self.REDIRECT_URI
        }
        # request for token
        
        response = requests.post(
            self.TOKEN_REQUEST_URI,
            data=params,
            headers=headers)
        
        if response.status_code != 200:
            raise Exception("Action unsuccessful " + str(response.status_code))
        # get the tokens
        response = response.json()
        token = dict()
        token['access_token'] = response['access_token']
        token['refresh_token'] = response['refresh_token']
        
        return token


    def RefreshToken(self, token):
        """ Refresh expired access token """
        # authentication header
        client_id = self.CLIENT_ID.encode('utf-8')
        secret = self.CLIENT_SECRET.encode('utf-8')
        headers = {
            'Authorization': os.environ.get('Authorization'),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # parameters for refresh token request
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': token['refresh_token']
        }
        # request for token
        response = requests.post(self.TOKEN_REQUEST_URI, data=params, headers=headers)
        if response.status_code != 200:
            raise Exception("Action unsuccessful")
        # replace tokens
        token['access_token'] = response.access_token
        token['refresh_token'] = response.refresh_token
        return token


    def GetWeight(self, token):
        """Method makes call to API"""
        headers = {
            'Authorization': 'Bearer ' + token['access_token']
        }
        url = os.getenv('url')
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            j = response.json()
            return response.json()


        elif response.status_code == 403:
            token = self.RefreshToken(token)
            self.GetWeight(token)

        else:
            raise Exception("Action unsuccessful")