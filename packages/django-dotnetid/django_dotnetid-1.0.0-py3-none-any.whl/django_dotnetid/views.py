import jwt
import logging

from django.conf import settings

from allauth.socialaccount.providers.openid_connect.views import OpenIDConnectOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)

from allauth.socialaccount.providers.oauth2.client import OAuth2Error

from .provider import DotnetIdProvider

LOGGER = logging.getLogger(__name__)

ID_TOKEN_ISSUER = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
        .get("dotnetidprovider", {})
        .get("ID_TOKEN_ISSUER")
)

EXTRA_ATTRIBUTES_PREFIX = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
        .get("dotnetidprovider", {})
        .get("EXTRA_ATTRIBUTES_PREFIX", "")
)

EXTRA_ATTRIBUTES_NAMES = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
        .get("dotnetidprovider", {})
        .get("EXTRA_ATTRIBUTES_NAMES", [])
)

class DotnetIdAdapter(OpenIDConnectOAuth2Adapter):
    provider_id = DotnetIdProvider.id

    def complete_login(self, request, app, token, response, **kwargs):
        try:
            identity_data = jwt.decode(
                response["id_token"],
                # Since the token was received by direct communication
                # protected by TLS between this library and dotnetaccess, we
                # are allowed to skip checking the token signature
                # according to the OpenID Connect Core 1.0
                # specification.
                # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=ID_TOKEN_ISSUER,
                audience=app.client_id,
            )
        except jwt.PyJWTError as e:
            LOGGER.error(f"Invalid id_token: {e}")
            raise OAuth2Error("Invalid id_token") from e

        identity_provider = identity_data['idp']
        extra_data = {
            "first_name": identity_data['given_name'],
            "last_name": identity_data['family_name'],
            "sub": identity_data['sub'],
            "idp": identity_provider,
        }
        
        match identity_provider:
            case "nech":
                extra_data['email'] = identity_data['upn']
                extra_data['username'] = identity_data['name'].replace("ACN\\", "")
                for attr in EXTRA_ATTRIBUTES_NAMES:
                    extra_attr = f"{EXTRA_ATTRIBUTES_PREFIX}.{attr}"
                    try:
                        extra_data[extra_attr] = identity_data[extra_attr]
                        
                    except KeyError as e:
                        LOGGER.error(f"{extra_attr} is defined in settings but not present in id_token.")
                        raise OAuth2Error(f"{extra_attr} is defined in settings but not present in id_token.")
            case "agov":
                extra_data['email'] = identity_data['email']
                extra_data['username'] = identity_data['email']
            case _:
                LOGGER.error(f"Unknown identity provider: {identity_provider}")

        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login

def login(request, provider_id):
    view = OAuth2LoginView.adapter_view(DotnetIdAdapter(request, provider_id))
    return view(request)


def callback(request, provider_id):
    view = OAuth2CallbackView.adapter_view(DotnetIdAdapter(request, provider_id))
    return view(request)
