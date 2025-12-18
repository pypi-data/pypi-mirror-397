# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
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
from ._version import __version__
from .resources import me, cnos, meta, authz, context, config_schema
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import CnosHubError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.admin import admin
from .resources.api_keys import api_keys
from .resources.projects import projects

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "CnosHub", "AsyncCnosHub", "Client", "AsyncClient"]


class CnosHub(SyncAPIClient):
    admin: admin.AdminResource
    cnos: cnos.CnosResource
    meta: meta.MetaResource
    authz: authz.AuthzResource
    config_schema: config_schema.ConfigSchemaResource
    me: me.MeResource
    context: context.ContextResource
    api_keys: api_keys.APIKeysResource
    projects: projects.ProjectsResource
    with_raw_response: CnosHubWithRawResponse
    with_streaming_response: CnosHubWithStreamedResponse

    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
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
        """Construct a new synchronous CnosHub client instance.

        This automatically infers the `bearer_token` argument from the `CNOS_HUB_API_KEY` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("CNOS_HUB_API_KEY")
        if bearer_token is None:
            raise CnosHubError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the CNOS_HUB_API_KEY environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("CNOS_HUB_BASE_URL")
        if base_url is None:
            base_url = f"https://api.example.com"

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

        self.admin = admin.AdminResource(self)
        self.cnos = cnos.CnosResource(self)
        self.meta = meta.MetaResource(self)
        self.authz = authz.AuthzResource(self)
        self.config_schema = config_schema.ConfigSchemaResource(self)
        self.me = me.MeResource(self)
        self.context = context.ContextResource(self)
        self.api_keys = api_keys.APIKeysResource(self)
        self.projects = projects.ProjectsResource(self)
        self.with_raw_response = CnosHubWithRawResponse(self)
        self.with_streaming_response = CnosHubWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

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
        bearer_token: str | None = None,
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
            bearer_token=bearer_token or self.bearer_token,
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


class AsyncCnosHub(AsyncAPIClient):
    admin: admin.AsyncAdminResource
    cnos: cnos.AsyncCnosResource
    meta: meta.AsyncMetaResource
    authz: authz.AsyncAuthzResource
    config_schema: config_schema.AsyncConfigSchemaResource
    me: me.AsyncMeResource
    context: context.AsyncContextResource
    api_keys: api_keys.AsyncAPIKeysResource
    projects: projects.AsyncProjectsResource
    with_raw_response: AsyncCnosHubWithRawResponse
    with_streaming_response: AsyncCnosHubWithStreamedResponse

    # client options
    bearer_token: str

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
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
        """Construct a new async AsyncCnosHub client instance.

        This automatically infers the `bearer_token` argument from the `CNOS_HUB_API_KEY` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("CNOS_HUB_API_KEY")
        if bearer_token is None:
            raise CnosHubError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the CNOS_HUB_API_KEY environment variable"
            )
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("CNOS_HUB_BASE_URL")
        if base_url is None:
            base_url = f"https://api.example.com"

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

        self.admin = admin.AsyncAdminResource(self)
        self.cnos = cnos.AsyncCnosResource(self)
        self.meta = meta.AsyncMetaResource(self)
        self.authz = authz.AsyncAuthzResource(self)
        self.config_schema = config_schema.AsyncConfigSchemaResource(self)
        self.me = me.AsyncMeResource(self)
        self.context = context.AsyncContextResource(self)
        self.api_keys = api_keys.AsyncAPIKeysResource(self)
        self.projects = projects.AsyncProjectsResource(self)
        self.with_raw_response = AsyncCnosHubWithRawResponse(self)
        self.with_streaming_response = AsyncCnosHubWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

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
        bearer_token: str | None = None,
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
            bearer_token=bearer_token or self.bearer_token,
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


class CnosHubWithRawResponse:
    def __init__(self, client: CnosHub) -> None:
        self.admin = admin.AdminResourceWithRawResponse(client.admin)
        self.cnos = cnos.CnosResourceWithRawResponse(client.cnos)
        self.meta = meta.MetaResourceWithRawResponse(client.meta)
        self.authz = authz.AuthzResourceWithRawResponse(client.authz)
        self.config_schema = config_schema.ConfigSchemaResourceWithRawResponse(client.config_schema)
        self.me = me.MeResourceWithRawResponse(client.me)
        self.context = context.ContextResourceWithRawResponse(client.context)
        self.api_keys = api_keys.APIKeysResourceWithRawResponse(client.api_keys)
        self.projects = projects.ProjectsResourceWithRawResponse(client.projects)


class AsyncCnosHubWithRawResponse:
    def __init__(self, client: AsyncCnosHub) -> None:
        self.admin = admin.AsyncAdminResourceWithRawResponse(client.admin)
        self.cnos = cnos.AsyncCnosResourceWithRawResponse(client.cnos)
        self.meta = meta.AsyncMetaResourceWithRawResponse(client.meta)
        self.authz = authz.AsyncAuthzResourceWithRawResponse(client.authz)
        self.config_schema = config_schema.AsyncConfigSchemaResourceWithRawResponse(client.config_schema)
        self.me = me.AsyncMeResourceWithRawResponse(client.me)
        self.context = context.AsyncContextResourceWithRawResponse(client.context)
        self.api_keys = api_keys.AsyncAPIKeysResourceWithRawResponse(client.api_keys)
        self.projects = projects.AsyncProjectsResourceWithRawResponse(client.projects)


class CnosHubWithStreamedResponse:
    def __init__(self, client: CnosHub) -> None:
        self.admin = admin.AdminResourceWithStreamingResponse(client.admin)
        self.cnos = cnos.CnosResourceWithStreamingResponse(client.cnos)
        self.meta = meta.MetaResourceWithStreamingResponse(client.meta)
        self.authz = authz.AuthzResourceWithStreamingResponse(client.authz)
        self.config_schema = config_schema.ConfigSchemaResourceWithStreamingResponse(client.config_schema)
        self.me = me.MeResourceWithStreamingResponse(client.me)
        self.context = context.ContextResourceWithStreamingResponse(client.context)
        self.api_keys = api_keys.APIKeysResourceWithStreamingResponse(client.api_keys)
        self.projects = projects.ProjectsResourceWithStreamingResponse(client.projects)


class AsyncCnosHubWithStreamedResponse:
    def __init__(self, client: AsyncCnosHub) -> None:
        self.admin = admin.AsyncAdminResourceWithStreamingResponse(client.admin)
        self.cnos = cnos.AsyncCnosResourceWithStreamingResponse(client.cnos)
        self.meta = meta.AsyncMetaResourceWithStreamingResponse(client.meta)
        self.authz = authz.AsyncAuthzResourceWithStreamingResponse(client.authz)
        self.config_schema = config_schema.AsyncConfigSchemaResourceWithStreamingResponse(client.config_schema)
        self.me = me.AsyncMeResourceWithStreamingResponse(client.me)
        self.context = context.AsyncContextResourceWithStreamingResponse(client.context)
        self.api_keys = api_keys.AsyncAPIKeysResourceWithStreamingResponse(client.api_keys)
        self.projects = projects.AsyncProjectsResourceWithStreamingResponse(client.projects)


Client = CnosHub

AsyncClient = AsyncCnosHub
