import threading
import logging
import os
import base64
import json
from datetime import datetime, timedelta, timezone
import time
from typing import Any

import across.sdk.v1 as sdk
from across.sdk.v1 import rest

from .abstract_credential_storage import CredentialStorage as ICredStorage

logger = logging.getLogger("ACROSS_API_CLIENT_WRAPPER")


class ApiClientWrapper(sdk.ApiClient):
    _client = None
    _cred_store: ICredStorage | None = None
    _exp: datetime | None = None

    def __init__(
        self,
        configuration: sdk.Configuration,
        creds_store: ICredStorage | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(configuration, *args, **kwargs)

        self._cred_store = creds_store
        self._lock = threading.Lock()

    @classmethod
    def get_client(
        cls,
        configuration: sdk.Configuration,
        creds: ICredStorage | None = None,
    ):
        """
        Retrieve (or lazily initialize) a singleton API client.

        This method ensures that only one client instance is created per class.
        If no client exists, it will initialize one using the provided
        `configuration` and optional `creds` (credentials storage).

        Credentials resolution order:
            1. Use `configuration.username` and `configuration.password` if they are provided.
            2. If not provided and `creds` is passed in, fetch credentials from it.
            3. Otherwise, fall back to environment variables:
                - `ACROSS_SERVER_ID`
                - `ACROSS_SERVER_SECRET`

        ⚠️ Note:
            This is a **singleton** accessor. Once the client is created,
            subsequent calls to `get_client` will reuse the same instance,
            regardless of whether a different `configuration` or `creds` is passed.
            To reset or replace the client, `_client` must be cleared explicitly.

        Args:
            configuration (sdk.Configuration): The base configuration object
                for the SDK client.
            creds (ICredStorage | None, optional): Optional credential storage
                provider for resolving `id` and `secret`. Defaults to None.

        Returns:
            ApiClientWrapper: A singleton instance of the API client wrapper.

        Example:
                from my_sdk import Configuration, ApiClientWrapper, CredentialStorage, SomeApi
                from my_creds import CredStorage

                config = Configuration(host="https://api.example.com")
                creds: CredentialStorage = CredStorage()

                client = ApiClientWrapper.get_client(configuration=config, creds=creds)

                response = SomeApi(client).some_method()
                print(response)
        """
        if cls._client is None:
            if not configuration.username and not configuration.password:
                # Use the creds store if it is passed in, otherwise use env vars
                if creds:
                    configuration.username = creds.id(force=True)
                    configuration.password = creds.secret(force=True)
                else:
                    configuration.username = os.getenv("ACROSS_SERVER_ID")
                    configuration.password = os.getenv("ACROSS_SERVER_SECRET")

            cls._client = ApiClientWrapper(
                configuration=configuration,
                creds_store=creds,
            )

        return cls._client

    def call_api(self, *args, **kwargs) -> rest.RESTResponse:
        if args[0].lower() != "get":
            self.refresh()

        try:
            return super().call_api(*args, **kwargs)
        except sdk.ApiException as err:
            if err.status == 401:
                logger.debug("Access token is unauthenticated or it has expired.")

                refreshed = self.refresh_token()

                # Attempt the call again
                if refreshed:
                    return super().call_api(*args, **kwargs)
                else:
                    raise err
            else:
                raise err

    def refresh(self) -> None:
        if not self.configuration.access_token:
            logger.debug('No access_token, refreshing')
            self.refresh_token()

        if self._is_token_invalid(self.configuration.access_token):
            logger.debug('Expired access_token, refreshing')
            self.refresh_token()

        if self._cred_store:
            with self._lock:
                if self._should_rotate(self._cred_store):
                    res = sdk.InternalApi(super()).service_account_rotate_key(
                        service_account_id=self._cred_store.id()
                    )

                    self._set_exp(res.expiration)
                    self._cred_store.update_key(res.secret_key)
                    self.configuration.password = res.secret_key

    

    def _decode_jwt_part(self, encoded_part) -> dict[str, Any]:
        """Decodes a Base64Url-encoded JWT part and returns the decoded JSON as a dictionary."""
        # Add padding characters if missing, as Base64Url encoding might omit them.
        # Base64 requires padding to be a multiple of 4.
        missing_padding = len(encoded_part) % 4
        if missing_padding != 0:
            encoded_part += '=' * (4 - missing_padding)

        # Decode from Base64Url to bytes to UTF-8
        decoded_bytes = base64.urlsafe_b64decode(encoded_part).decode('utf-8')

        if decoded_bytes is None:
            logger.debug("Could not decode jwt payload as bytes")
            return {}

        decoded_json = json.loads(decoded_bytes)
        return decoded_json

    def _is_token_invalid(self, jwt_token):
        """Returns True when the token is expired, malformed, or missing expiration"""
        # JWT contains 3 parts, we're looking for the middle part; the payload with the exp key
        if not isinstance(jwt_token, str):
            return True
        
        jwt_parts = jwt_token.split('.')

        if len(jwt_parts) != 3:
            return True

        payload_encoded = jwt_parts[1]

        if payload_encoded is None:
            logger.debug("Token missing payload")
            return True

        payload = self._decode_jwt_part(payload_encoded)
        token_exp = payload.get('exp')
        current_timestamp = time.time()

        if token_exp is None:
            logger.debug("Token missing exp")
            return True

        # Add 30 seconds to avoid boundary condition expiry while request is in flight
        if token_exp < current_timestamp + 30:
            logger.debug("Token is expired")
            return True
        
        return False
        

    def refresh_token(self) -> bool:
        if self.configuration.username and self.configuration.password:
            logger.debug("Refreshing access token...")

            # Instantiate with super to avoid infinite recursion through call_api
            token = sdk.AuthApi(super()).token(
                grant_type=sdk.GrantType.CLIENT_CREDENTIALS
            )

            self.configuration.access_token = token.access_token

            logger.debug("Successfully refreshed token!")

            return True

        return False

    def _should_rotate(self, cred_store: ICredStorage) -> bool:
        now = datetime.now(timezone.utc)

        expiration = self._expiration(cred_store)

        if expiration:
            will_expire_soon = expiration <= now + timedelta(
                days=cred_store.days_before_exp
            )

            return will_expire_soon

        return True

    def _expiration(self, cred_store: ICredStorage) -> datetime | None:
        if self._exp:
            return self._exp

        res = sdk.InternalApi(super()).get_service_account(
            service_account_id=cred_store.id()
        )

        self._set_exp(res.expiration)

        return self._exp

    def _set_exp(self, date: datetime):
        if date.tzinfo is None:
            self._exp = date.replace(tzinfo=timezone.utc)
        else:
            self._exp = date
