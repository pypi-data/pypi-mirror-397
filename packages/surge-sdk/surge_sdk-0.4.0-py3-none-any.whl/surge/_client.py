# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import SurgeError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import users, blasts, accounts, contacts, messages, campaigns, phone_numbers, verifications
    from .resources.users import UsersResource, AsyncUsersResource
    from .resources.blasts import BlastsResource, AsyncBlastsResource
    from .resources.accounts import AccountsResource, AsyncAccountsResource
    from .resources.contacts import ContactsResource, AsyncContactsResource
    from .resources.messages import MessagesResource, AsyncMessagesResource
    from .resources.webhooks import WebhooksResource, AsyncWebhooksResource
    from .resources.campaigns import CampaignsResource, AsyncCampaignsResource
    from .resources.phone_numbers import PhoneNumbersResource, AsyncPhoneNumbersResource
    from .resources.verifications import VerificationsResource, AsyncVerificationsResource

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Surge", "AsyncSurge", "Client", "AsyncClient"]


class Surge(SyncAPIClient):
    # client options
    api_key: str
    webhook_signing_secret: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Surge client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `SURGE_API_KEY`
        - `webhook_signing_secret` from `SURGE_WEBHOOK_SIGNING_SECRET`
        """
        if api_key is None:
            api_key = os.environ.get("SURGE_API_KEY")
        if api_key is None:
            raise SurgeError(
                "The api_key client option must be set either by passing api_key to the client or by setting the SURGE_API_KEY environment variable"
            )
        self.api_key = api_key

        if webhook_signing_secret is None:
            webhook_signing_secret = os.environ.get("SURGE_WEBHOOK_SIGNING_SECRET")
        self.webhook_signing_secret = webhook_signing_secret

        if base_url is None:
            base_url = os.environ.get("SURGE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.surge.app"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def accounts(self) -> AccountsResource:
        from .resources.accounts import AccountsResource

        return AccountsResource(self)

    @cached_property
    def blasts(self) -> BlastsResource:
        from .resources.blasts import BlastsResource

        return BlastsResource(self)

    @cached_property
    def campaigns(self) -> CampaignsResource:
        from .resources.campaigns import CampaignsResource

        return CampaignsResource(self)

    @cached_property
    def contacts(self) -> ContactsResource:
        from .resources.contacts import ContactsResource

        return ContactsResource(self)

    @cached_property
    def messages(self) -> MessagesResource:
        from .resources.messages import MessagesResource

        return MessagesResource(self)

    @cached_property
    def phone_numbers(self) -> PhoneNumbersResource:
        from .resources.phone_numbers import PhoneNumbersResource

        return PhoneNumbersResource(self)

    @cached_property
    def users(self) -> UsersResource:
        from .resources.users import UsersResource

        return UsersResource(self)

    @cached_property
    def verifications(self) -> VerificationsResource:
        from .resources.verifications import VerificationsResource

        return VerificationsResource(self)

    @cached_property
    def webhooks(self) -> WebhooksResource:
        from .resources.webhooks import WebhooksResource

        return WebhooksResource(self)

    @cached_property
    def with_raw_response(self) -> SurgeWithRawResponse:
        return SurgeWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SurgeWithStreamedResponse:
        return SurgeWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            webhook_signing_secret=webhook_signing_secret or self.webhook_signing_secret,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncSurge(AsyncAPIClient):
    # client options
    api_key: str
    webhook_signing_secret: str | None

    def __init__(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncSurge client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `SURGE_API_KEY`
        - `webhook_signing_secret` from `SURGE_WEBHOOK_SIGNING_SECRET`
        """
        if api_key is None:
            api_key = os.environ.get("SURGE_API_KEY")
        if api_key is None:
            raise SurgeError(
                "The api_key client option must be set either by passing api_key to the client or by setting the SURGE_API_KEY environment variable"
            )
        self.api_key = api_key

        if webhook_signing_secret is None:
            webhook_signing_secret = os.environ.get("SURGE_WEBHOOK_SIGNING_SECRET")
        self.webhook_signing_secret = webhook_signing_secret

        if base_url is None:
            base_url = os.environ.get("SURGE_BASE_URL")
        if base_url is None:
            base_url = f"https://api.surge.app"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def accounts(self) -> AsyncAccountsResource:
        from .resources.accounts import AsyncAccountsResource

        return AsyncAccountsResource(self)

    @cached_property
    def blasts(self) -> AsyncBlastsResource:
        from .resources.blasts import AsyncBlastsResource

        return AsyncBlastsResource(self)

    @cached_property
    def campaigns(self) -> AsyncCampaignsResource:
        from .resources.campaigns import AsyncCampaignsResource

        return AsyncCampaignsResource(self)

    @cached_property
    def contacts(self) -> AsyncContactsResource:
        from .resources.contacts import AsyncContactsResource

        return AsyncContactsResource(self)

    @cached_property
    def messages(self) -> AsyncMessagesResource:
        from .resources.messages import AsyncMessagesResource

        return AsyncMessagesResource(self)

    @cached_property
    def phone_numbers(self) -> AsyncPhoneNumbersResource:
        from .resources.phone_numbers import AsyncPhoneNumbersResource

        return AsyncPhoneNumbersResource(self)

    @cached_property
    def users(self) -> AsyncUsersResource:
        from .resources.users import AsyncUsersResource

        return AsyncUsersResource(self)

    @cached_property
    def verifications(self) -> AsyncVerificationsResource:
        from .resources.verifications import AsyncVerificationsResource

        return AsyncVerificationsResource(self)

    @cached_property
    def webhooks(self) -> AsyncWebhooksResource:
        from .resources.webhooks import AsyncWebhooksResource

        return AsyncWebhooksResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncSurgeWithRawResponse:
        return AsyncSurgeWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSurgeWithStreamedResponse:
        return AsyncSurgeWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        webhook_signing_secret: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            webhook_signing_secret=webhook_signing_secret or self.webhook_signing_secret,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class SurgeWithRawResponse:
    _client: Surge

    def __init__(self, client: Surge) -> None:
        self._client = client

    @cached_property
    def accounts(self) -> accounts.AccountsResourceWithRawResponse:
        from .resources.accounts import AccountsResourceWithRawResponse

        return AccountsResourceWithRawResponse(self._client.accounts)

    @cached_property
    def blasts(self) -> blasts.BlastsResourceWithRawResponse:
        from .resources.blasts import BlastsResourceWithRawResponse

        return BlastsResourceWithRawResponse(self._client.blasts)

    @cached_property
    def campaigns(self) -> campaigns.CampaignsResourceWithRawResponse:
        from .resources.campaigns import CampaignsResourceWithRawResponse

        return CampaignsResourceWithRawResponse(self._client.campaigns)

    @cached_property
    def contacts(self) -> contacts.ContactsResourceWithRawResponse:
        from .resources.contacts import ContactsResourceWithRawResponse

        return ContactsResourceWithRawResponse(self._client.contacts)

    @cached_property
    def messages(self) -> messages.MessagesResourceWithRawResponse:
        from .resources.messages import MessagesResourceWithRawResponse

        return MessagesResourceWithRawResponse(self._client.messages)

    @cached_property
    def phone_numbers(self) -> phone_numbers.PhoneNumbersResourceWithRawResponse:
        from .resources.phone_numbers import PhoneNumbersResourceWithRawResponse

        return PhoneNumbersResourceWithRawResponse(self._client.phone_numbers)

    @cached_property
    def users(self) -> users.UsersResourceWithRawResponse:
        from .resources.users import UsersResourceWithRawResponse

        return UsersResourceWithRawResponse(self._client.users)

    @cached_property
    def verifications(self) -> verifications.VerificationsResourceWithRawResponse:
        from .resources.verifications import VerificationsResourceWithRawResponse

        return VerificationsResourceWithRawResponse(self._client.verifications)


class AsyncSurgeWithRawResponse:
    _client: AsyncSurge

    def __init__(self, client: AsyncSurge) -> None:
        self._client = client

    @cached_property
    def accounts(self) -> accounts.AsyncAccountsResourceWithRawResponse:
        from .resources.accounts import AsyncAccountsResourceWithRawResponse

        return AsyncAccountsResourceWithRawResponse(self._client.accounts)

    @cached_property
    def blasts(self) -> blasts.AsyncBlastsResourceWithRawResponse:
        from .resources.blasts import AsyncBlastsResourceWithRawResponse

        return AsyncBlastsResourceWithRawResponse(self._client.blasts)

    @cached_property
    def campaigns(self) -> campaigns.AsyncCampaignsResourceWithRawResponse:
        from .resources.campaigns import AsyncCampaignsResourceWithRawResponse

        return AsyncCampaignsResourceWithRawResponse(self._client.campaigns)

    @cached_property
    def contacts(self) -> contacts.AsyncContactsResourceWithRawResponse:
        from .resources.contacts import AsyncContactsResourceWithRawResponse

        return AsyncContactsResourceWithRawResponse(self._client.contacts)

    @cached_property
    def messages(self) -> messages.AsyncMessagesResourceWithRawResponse:
        from .resources.messages import AsyncMessagesResourceWithRawResponse

        return AsyncMessagesResourceWithRawResponse(self._client.messages)

    @cached_property
    def phone_numbers(self) -> phone_numbers.AsyncPhoneNumbersResourceWithRawResponse:
        from .resources.phone_numbers import AsyncPhoneNumbersResourceWithRawResponse

        return AsyncPhoneNumbersResourceWithRawResponse(self._client.phone_numbers)

    @cached_property
    def users(self) -> users.AsyncUsersResourceWithRawResponse:
        from .resources.users import AsyncUsersResourceWithRawResponse

        return AsyncUsersResourceWithRawResponse(self._client.users)

    @cached_property
    def verifications(self) -> verifications.AsyncVerificationsResourceWithRawResponse:
        from .resources.verifications import AsyncVerificationsResourceWithRawResponse

        return AsyncVerificationsResourceWithRawResponse(self._client.verifications)


class SurgeWithStreamedResponse:
    _client: Surge

    def __init__(self, client: Surge) -> None:
        self._client = client

    @cached_property
    def accounts(self) -> accounts.AccountsResourceWithStreamingResponse:
        from .resources.accounts import AccountsResourceWithStreamingResponse

        return AccountsResourceWithStreamingResponse(self._client.accounts)

    @cached_property
    def blasts(self) -> blasts.BlastsResourceWithStreamingResponse:
        from .resources.blasts import BlastsResourceWithStreamingResponse

        return BlastsResourceWithStreamingResponse(self._client.blasts)

    @cached_property
    def campaigns(self) -> campaigns.CampaignsResourceWithStreamingResponse:
        from .resources.campaigns import CampaignsResourceWithStreamingResponse

        return CampaignsResourceWithStreamingResponse(self._client.campaigns)

    @cached_property
    def contacts(self) -> contacts.ContactsResourceWithStreamingResponse:
        from .resources.contacts import ContactsResourceWithStreamingResponse

        return ContactsResourceWithStreamingResponse(self._client.contacts)

    @cached_property
    def messages(self) -> messages.MessagesResourceWithStreamingResponse:
        from .resources.messages import MessagesResourceWithStreamingResponse

        return MessagesResourceWithStreamingResponse(self._client.messages)

    @cached_property
    def phone_numbers(self) -> phone_numbers.PhoneNumbersResourceWithStreamingResponse:
        from .resources.phone_numbers import PhoneNumbersResourceWithStreamingResponse

        return PhoneNumbersResourceWithStreamingResponse(self._client.phone_numbers)

    @cached_property
    def users(self) -> users.UsersResourceWithStreamingResponse:
        from .resources.users import UsersResourceWithStreamingResponse

        return UsersResourceWithStreamingResponse(self._client.users)

    @cached_property
    def verifications(self) -> verifications.VerificationsResourceWithStreamingResponse:
        from .resources.verifications import VerificationsResourceWithStreamingResponse

        return VerificationsResourceWithStreamingResponse(self._client.verifications)


class AsyncSurgeWithStreamedResponse:
    _client: AsyncSurge

    def __init__(self, client: AsyncSurge) -> None:
        self._client = client

    @cached_property
    def accounts(self) -> accounts.AsyncAccountsResourceWithStreamingResponse:
        from .resources.accounts import AsyncAccountsResourceWithStreamingResponse

        return AsyncAccountsResourceWithStreamingResponse(self._client.accounts)

    @cached_property
    def blasts(self) -> blasts.AsyncBlastsResourceWithStreamingResponse:
        from .resources.blasts import AsyncBlastsResourceWithStreamingResponse

        return AsyncBlastsResourceWithStreamingResponse(self._client.blasts)

    @cached_property
    def campaigns(self) -> campaigns.AsyncCampaignsResourceWithStreamingResponse:
        from .resources.campaigns import AsyncCampaignsResourceWithStreamingResponse

        return AsyncCampaignsResourceWithStreamingResponse(self._client.campaigns)

    @cached_property
    def contacts(self) -> contacts.AsyncContactsResourceWithStreamingResponse:
        from .resources.contacts import AsyncContactsResourceWithStreamingResponse

        return AsyncContactsResourceWithStreamingResponse(self._client.contacts)

    @cached_property
    def messages(self) -> messages.AsyncMessagesResourceWithStreamingResponse:
        from .resources.messages import AsyncMessagesResourceWithStreamingResponse

        return AsyncMessagesResourceWithStreamingResponse(self._client.messages)

    @cached_property
    def phone_numbers(self) -> phone_numbers.AsyncPhoneNumbersResourceWithStreamingResponse:
        from .resources.phone_numbers import AsyncPhoneNumbersResourceWithStreamingResponse

        return AsyncPhoneNumbersResourceWithStreamingResponse(self._client.phone_numbers)

    @cached_property
    def users(self) -> users.AsyncUsersResourceWithStreamingResponse:
        from .resources.users import AsyncUsersResourceWithStreamingResponse

        return AsyncUsersResourceWithStreamingResponse(self._client.users)

    @cached_property
    def verifications(self) -> verifications.AsyncVerificationsResourceWithStreamingResponse:
        from .resources.verifications import AsyncVerificationsResourceWithStreamingResponse

        return AsyncVerificationsResourceWithStreamingResponse(self._client.verifications)


Client = Surge

AsyncClient = AsyncSurge
