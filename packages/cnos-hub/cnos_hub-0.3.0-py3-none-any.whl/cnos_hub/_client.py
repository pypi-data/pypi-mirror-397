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
from ._exceptions import CnosHubError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import me, cnos, meta, admin, authz, context, api_keys, projects, config_schema
    from .resources.me import MeResource, AsyncMeResource
    from .resources.cnos import CnosResource, AsyncCnosResource
    from .resources.meta import MetaResource, AsyncMetaResource
    from .resources.authz import AuthzResource, AsyncAuthzResource
    from .resources.context import ContextResource, AsyncContextResource
    from .resources.admin.admin import AdminResource, AsyncAdminResource
    from .resources.config_schema import ConfigSchemaResource, AsyncConfigSchemaResource
    from .resources.api_keys.api_keys import APIKeysResource, AsyncAPIKeysResource
    from .resources.projects.projects import ProjectsResource, AsyncProjectsResource

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "CnosHub", "AsyncCnosHub", "Client", "AsyncClient"]


class CnosHub(SyncAPIClient):
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

    @cached_property
    def admin(self) -> AdminResource:
        from .resources.admin import AdminResource

        return AdminResource(self)

    @cached_property
    def cnos(self) -> CnosResource:
        from .resources.cnos import CnosResource

        return CnosResource(self)

    @cached_property
    def meta(self) -> MetaResource:
        from .resources.meta import MetaResource

        return MetaResource(self)

    @cached_property
    def authz(self) -> AuthzResource:
        from .resources.authz import AuthzResource

        return AuthzResource(self)

    @cached_property
    def config_schema(self) -> ConfigSchemaResource:
        from .resources.config_schema import ConfigSchemaResource

        return ConfigSchemaResource(self)

    @cached_property
    def me(self) -> MeResource:
        from .resources.me import MeResource

        return MeResource(self)

    @cached_property
    def context(self) -> ContextResource:
        from .resources.context import ContextResource

        return ContextResource(self)

    @cached_property
    def api_keys(self) -> APIKeysResource:
        from .resources.api_keys import APIKeysResource

        return APIKeysResource(self)

    @cached_property
    def projects(self) -> ProjectsResource:
        from .resources.projects import ProjectsResource

        return ProjectsResource(self)

    @cached_property
    def with_raw_response(self) -> CnosHubWithRawResponse:
        return CnosHubWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CnosHubWithStreamedResponse:
        return CnosHubWithStreamedResponse(self)

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

    @cached_property
    def admin(self) -> AsyncAdminResource:
        from .resources.admin import AsyncAdminResource

        return AsyncAdminResource(self)

    @cached_property
    def cnos(self) -> AsyncCnosResource:
        from .resources.cnos import AsyncCnosResource

        return AsyncCnosResource(self)

    @cached_property
    def meta(self) -> AsyncMetaResource:
        from .resources.meta import AsyncMetaResource

        return AsyncMetaResource(self)

    @cached_property
    def authz(self) -> AsyncAuthzResource:
        from .resources.authz import AsyncAuthzResource

        return AsyncAuthzResource(self)

    @cached_property
    def config_schema(self) -> AsyncConfigSchemaResource:
        from .resources.config_schema import AsyncConfigSchemaResource

        return AsyncConfigSchemaResource(self)

    @cached_property
    def me(self) -> AsyncMeResource:
        from .resources.me import AsyncMeResource

        return AsyncMeResource(self)

    @cached_property
    def context(self) -> AsyncContextResource:
        from .resources.context import AsyncContextResource

        return AsyncContextResource(self)

    @cached_property
    def api_keys(self) -> AsyncAPIKeysResource:
        from .resources.api_keys import AsyncAPIKeysResource

        return AsyncAPIKeysResource(self)

    @cached_property
    def projects(self) -> AsyncProjectsResource:
        from .resources.projects import AsyncProjectsResource

        return AsyncProjectsResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncCnosHubWithRawResponse:
        return AsyncCnosHubWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCnosHubWithStreamedResponse:
        return AsyncCnosHubWithStreamedResponse(self)

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
    _client: CnosHub

    def __init__(self, client: CnosHub) -> None:
        self._client = client

    @cached_property
    def admin(self) -> admin.AdminResourceWithRawResponse:
        from .resources.admin import AdminResourceWithRawResponse

        return AdminResourceWithRawResponse(self._client.admin)

    @cached_property
    def cnos(self) -> cnos.CnosResourceWithRawResponse:
        from .resources.cnos import CnosResourceWithRawResponse

        return CnosResourceWithRawResponse(self._client.cnos)

    @cached_property
    def meta(self) -> meta.MetaResourceWithRawResponse:
        from .resources.meta import MetaResourceWithRawResponse

        return MetaResourceWithRawResponse(self._client.meta)

    @cached_property
    def authz(self) -> authz.AuthzResourceWithRawResponse:
        from .resources.authz import AuthzResourceWithRawResponse

        return AuthzResourceWithRawResponse(self._client.authz)

    @cached_property
    def config_schema(self) -> config_schema.ConfigSchemaResourceWithRawResponse:
        from .resources.config_schema import ConfigSchemaResourceWithRawResponse

        return ConfigSchemaResourceWithRawResponse(self._client.config_schema)

    @cached_property
    def me(self) -> me.MeResourceWithRawResponse:
        from .resources.me import MeResourceWithRawResponse

        return MeResourceWithRawResponse(self._client.me)

    @cached_property
    def context(self) -> context.ContextResourceWithRawResponse:
        from .resources.context import ContextResourceWithRawResponse

        return ContextResourceWithRawResponse(self._client.context)

    @cached_property
    def api_keys(self) -> api_keys.APIKeysResourceWithRawResponse:
        from .resources.api_keys import APIKeysResourceWithRawResponse

        return APIKeysResourceWithRawResponse(self._client.api_keys)

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithRawResponse:
        from .resources.projects import ProjectsResourceWithRawResponse

        return ProjectsResourceWithRawResponse(self._client.projects)


class AsyncCnosHubWithRawResponse:
    _client: AsyncCnosHub

    def __init__(self, client: AsyncCnosHub) -> None:
        self._client = client

    @cached_property
    def admin(self) -> admin.AsyncAdminResourceWithRawResponse:
        from .resources.admin import AsyncAdminResourceWithRawResponse

        return AsyncAdminResourceWithRawResponse(self._client.admin)

    @cached_property
    def cnos(self) -> cnos.AsyncCnosResourceWithRawResponse:
        from .resources.cnos import AsyncCnosResourceWithRawResponse

        return AsyncCnosResourceWithRawResponse(self._client.cnos)

    @cached_property
    def meta(self) -> meta.AsyncMetaResourceWithRawResponse:
        from .resources.meta import AsyncMetaResourceWithRawResponse

        return AsyncMetaResourceWithRawResponse(self._client.meta)

    @cached_property
    def authz(self) -> authz.AsyncAuthzResourceWithRawResponse:
        from .resources.authz import AsyncAuthzResourceWithRawResponse

        return AsyncAuthzResourceWithRawResponse(self._client.authz)

    @cached_property
    def config_schema(self) -> config_schema.AsyncConfigSchemaResourceWithRawResponse:
        from .resources.config_schema import AsyncConfigSchemaResourceWithRawResponse

        return AsyncConfigSchemaResourceWithRawResponse(self._client.config_schema)

    @cached_property
    def me(self) -> me.AsyncMeResourceWithRawResponse:
        from .resources.me import AsyncMeResourceWithRawResponse

        return AsyncMeResourceWithRawResponse(self._client.me)

    @cached_property
    def context(self) -> context.AsyncContextResourceWithRawResponse:
        from .resources.context import AsyncContextResourceWithRawResponse

        return AsyncContextResourceWithRawResponse(self._client.context)

    @cached_property
    def api_keys(self) -> api_keys.AsyncAPIKeysResourceWithRawResponse:
        from .resources.api_keys import AsyncAPIKeysResourceWithRawResponse

        return AsyncAPIKeysResourceWithRawResponse(self._client.api_keys)

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithRawResponse:
        from .resources.projects import AsyncProjectsResourceWithRawResponse

        return AsyncProjectsResourceWithRawResponse(self._client.projects)


class CnosHubWithStreamedResponse:
    _client: CnosHub

    def __init__(self, client: CnosHub) -> None:
        self._client = client

    @cached_property
    def admin(self) -> admin.AdminResourceWithStreamingResponse:
        from .resources.admin import AdminResourceWithStreamingResponse

        return AdminResourceWithStreamingResponse(self._client.admin)

    @cached_property
    def cnos(self) -> cnos.CnosResourceWithStreamingResponse:
        from .resources.cnos import CnosResourceWithStreamingResponse

        return CnosResourceWithStreamingResponse(self._client.cnos)

    @cached_property
    def meta(self) -> meta.MetaResourceWithStreamingResponse:
        from .resources.meta import MetaResourceWithStreamingResponse

        return MetaResourceWithStreamingResponse(self._client.meta)

    @cached_property
    def authz(self) -> authz.AuthzResourceWithStreamingResponse:
        from .resources.authz import AuthzResourceWithStreamingResponse

        return AuthzResourceWithStreamingResponse(self._client.authz)

    @cached_property
    def config_schema(self) -> config_schema.ConfigSchemaResourceWithStreamingResponse:
        from .resources.config_schema import ConfigSchemaResourceWithStreamingResponse

        return ConfigSchemaResourceWithStreamingResponse(self._client.config_schema)

    @cached_property
    def me(self) -> me.MeResourceWithStreamingResponse:
        from .resources.me import MeResourceWithStreamingResponse

        return MeResourceWithStreamingResponse(self._client.me)

    @cached_property
    def context(self) -> context.ContextResourceWithStreamingResponse:
        from .resources.context import ContextResourceWithStreamingResponse

        return ContextResourceWithStreamingResponse(self._client.context)

    @cached_property
    def api_keys(self) -> api_keys.APIKeysResourceWithStreamingResponse:
        from .resources.api_keys import APIKeysResourceWithStreamingResponse

        return APIKeysResourceWithStreamingResponse(self._client.api_keys)

    @cached_property
    def projects(self) -> projects.ProjectsResourceWithStreamingResponse:
        from .resources.projects import ProjectsResourceWithStreamingResponse

        return ProjectsResourceWithStreamingResponse(self._client.projects)


class AsyncCnosHubWithStreamedResponse:
    _client: AsyncCnosHub

    def __init__(self, client: AsyncCnosHub) -> None:
        self._client = client

    @cached_property
    def admin(self) -> admin.AsyncAdminResourceWithStreamingResponse:
        from .resources.admin import AsyncAdminResourceWithStreamingResponse

        return AsyncAdminResourceWithStreamingResponse(self._client.admin)

    @cached_property
    def cnos(self) -> cnos.AsyncCnosResourceWithStreamingResponse:
        from .resources.cnos import AsyncCnosResourceWithStreamingResponse

        return AsyncCnosResourceWithStreamingResponse(self._client.cnos)

    @cached_property
    def meta(self) -> meta.AsyncMetaResourceWithStreamingResponse:
        from .resources.meta import AsyncMetaResourceWithStreamingResponse

        return AsyncMetaResourceWithStreamingResponse(self._client.meta)

    @cached_property
    def authz(self) -> authz.AsyncAuthzResourceWithStreamingResponse:
        from .resources.authz import AsyncAuthzResourceWithStreamingResponse

        return AsyncAuthzResourceWithStreamingResponse(self._client.authz)

    @cached_property
    def config_schema(self) -> config_schema.AsyncConfigSchemaResourceWithStreamingResponse:
        from .resources.config_schema import AsyncConfigSchemaResourceWithStreamingResponse

        return AsyncConfigSchemaResourceWithStreamingResponse(self._client.config_schema)

    @cached_property
    def me(self) -> me.AsyncMeResourceWithStreamingResponse:
        from .resources.me import AsyncMeResourceWithStreamingResponse

        return AsyncMeResourceWithStreamingResponse(self._client.me)

    @cached_property
    def context(self) -> context.AsyncContextResourceWithStreamingResponse:
        from .resources.context import AsyncContextResourceWithStreamingResponse

        return AsyncContextResourceWithStreamingResponse(self._client.context)

    @cached_property
    def api_keys(self) -> api_keys.AsyncAPIKeysResourceWithStreamingResponse:
        from .resources.api_keys import AsyncAPIKeysResourceWithStreamingResponse

        return AsyncAPIKeysResourceWithStreamingResponse(self._client.api_keys)

    @cached_property
    def projects(self) -> projects.AsyncProjectsResourceWithStreamingResponse:
        from .resources.projects import AsyncProjectsResourceWithStreamingResponse

        return AsyncProjectsResourceWithStreamingResponse(self._client.projects)


Client = CnosHub

AsyncClient = AsyncCnosHub
