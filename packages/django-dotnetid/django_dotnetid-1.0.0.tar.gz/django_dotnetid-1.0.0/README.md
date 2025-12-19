# django-dotnetid

django-dotnetid is a Django app extending django-allauth.
It implements an OpenID connect provider able to map extra_info from the id_token
into Django User model. It is also capable of attributing groups automatically.

You need to install django-allauth to be able to use this extension.

A full working example can be found here: https://github.com/sitn/django-dotnetid-example

## Quick start

1. Install requiremed packages in your project:

```sh
python -m pip install django-allauth pyjwt cryptography django-dotnetid
```

2. Add `django_dotnetid` to your INSTALLED_APPS setting like this:

```python
    INSTALLED_APPS = [
        ...,
        "django_dotnetid",
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
        "allauth.socialaccount.providers.openid_connect",
    ]
```

3. Include the dotnetidprovider URL conf in your project urls.py like this:

```python
from django.urls import include, path
...
    path('accounts/', include('allauth.urls')),
```

4. Run `python manage.py migrate` to create the models.

5. In your settings.py, you can add the provider like that:

```python
    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    ]

    SOCIALACCOUNT_PROVIDERS = {
        "dotnetidprovider": {
            "APP": {
                "provider_id": "dotnetid",
                "name": "Etat de Neuchâtel",
                "client_id": os.environ['DOTNETID_CLIENT_ID'],
                "secret": os.environ['DOTNETID_CLIENT_SECRET'],
                "settings": {
                    "server_url": os.environ['DOTNETID_SERVER_URL'],
                },
            },
            "SCOPE": [
                "profile",
                "openid",
                "glados",
            ],
            "EXTRA_ATTRIBUTES_PREFIX": "djangoopenid",
            "EXTRA_ATTRIBUTES_NAMES": [
                "groups",
                "admin",
            ],
            "OAUTH_PKCE_ENABLED": True,
            "ID_TOKEN_ISSUER": os.environ['DOTNETID_SERVER_URL'],
        }
    }
    SOCIALACCOUNT_EMAIL_VERIFICATION = None
    SOCIALACCOUNT_ADAPTER  = 'django_dotnetid.adapter.DotnetIdAccountAdapter'
    LOGIN_REDIRECT_URL = 'index'
    ACCOUNT_LOGOUT_REDIRECT = 'index'
    SITE_ID = 1
```

6.

Add `allauth.account.middleware.AccountMiddleware` at the end of your middlewares:

```python
MIDDLEWARE = [
...
    "allauth.account.middleware.AccountMiddleware",
]
```

7. Start the development server.

8. Visit the ``/``.
