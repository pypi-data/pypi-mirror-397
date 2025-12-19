from allauth.socialaccount import providers
from allauth.socialaccount.providers.openid_connect.provider import OpenIDConnectProviderAccount
from allauth.socialaccount.providers.openid_connect.provider import OpenIDConnectProvider


class DotnetIdAccount(OpenIDConnectProviderAccount):
    pass


class DotnetIdProvider(OpenIDConnectProvider):

    id = 'dotnetidprovider'
    name = 'Dotnet Id Provider'
    account_class = DotnetIdAccount


providers.registry.register(DotnetIdProvider)
