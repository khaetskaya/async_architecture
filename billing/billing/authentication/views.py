from urllib.parse import urlencode
from django.shortcuts import redirect

import requests
from oauthlib.common import generate_token
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

CODE_VERIFIER = generate_token()
OAUTH_CLIENT_ID = 'Vdmm4rP4pxeyKRNnKtXY2TFxtHUadwjTEbQRu9br'
OAUTH_CLIENT_SECRET = 'GNTlsE7kvosNmOcj2BSK8qAZ2Cvbx4c8PRwQHUGwxbXV82djxmQuzmaiTtCyRcRHfkFsojRZOsxzR52OMc2kyr2Cs6yeUpcXeBMYwGZbQqCYLaFdiwNlZkqJ41H4lnt4'


class AuthLoginView(APIView):
    def get(self, request):
        # Authentication service details
        auth_service_base_url = 'http://localhost:8000'
        redirect_uri = 'http://localhost:9000/api/callback'  # URL to handle the callback after authentication

        code_challenge_bytes = hashes.Hash(hashes.SHA256())
        code_challenge_bytes.update(CODE_VERIFIER.encode())
        code_challenge_digest = code_challenge_bytes.finalize()
        code_challenge = urlsafe_b64encode(code_challenge_digest).rstrip(b'=').decode()

        # Redirect the user to the authentication service login page
        params = {
            'client_id': OAUTH_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }

        login_url = f'{auth_service_base_url}/o/authorize/?{urlencode(params)}'
        return redirect(login_url)


class AuthCallbackView(APIView):
    def get(self, request):
        # Extract the authorization code from the query parameters
        auth_code = request.GET.get('code')

        # Authentication service details
        auth_service_token_url = 'http://localhost:8000/o/token/'
        redirect_uri = 'http://localhost:8080/api/callback'  # Redirect URI used during login

        # Exchange the authorization code for an access token
        data = {
            'code': auth_code,
            'grant_type': 'authorization_code',
            'client_id': OAUTH_CLIENT_ID,
            'client_secret': OAUTH_CLIENT_SECRET,
            'code_verifier': CODE_VERIFIER,
            'redirect_uri': redirect_uri,
        }

        response = requests.post(auth_service_token_url, data=data)

        if response.status_code == status.HTTP_200_OK:
            access_token = response.json().get('access_token')
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to exchange authorization code for access token'}, status=status.HTTP_400_BAD_REQUEST)


class AuthRedirectView(APIView):
    def get(self, request):
        access_token = request.GET.get('access_token')

        if access_token:
            # Use the access token for authentication or further processing
            # For example, you can save the access token in the session or use it for API requests

            return Response({'message': 'Authentication successful', 'access_token': access_token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Access token not found in callback URL'}, status=status.HTTP_400_BAD_REQUEST)


class AuthLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        access_token = request.data.get('access_token')
        oauth_server_url = 'http://localhost:8000/o/revoke-token/'
        oauth_payload = {
            'token': access_token,
            'client_id': OAUTH_CLIENT_ID,
            'client_secret': OAUTH_CLIENT_SECRET
        }
        response = requests.post(oauth_server_url, data=oauth_payload)

        if response.status_code == 200:
            return Response({'message': 'User successfully logged out from the resource service.'})
        else:
            return Response({'error': 'An error occurred while logging out. Please try again.'}, status=response.status_code)