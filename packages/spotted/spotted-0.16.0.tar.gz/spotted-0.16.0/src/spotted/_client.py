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
from ._oauth2 import OAuth2ClientCredentials, make_oauth2
from ._version import __version__
from .resources import (
    shows,
    albums,
    search,
    tracks,
    artists,
    markets,
    chapters,
    episodes,
    audiobooks,
    audio_analysis,
    audio_features,
    recommendations,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.me import me
from .resources.users import users
from .resources.browse import browse
from .resources.playlists import playlists

__all__ = ["Timeout", "Transport", "ProxiesTypes", "RequestOptions", "Spotted", "AsyncSpotted", "Client", "AsyncClient"]


class Spotted(SyncAPIClient):
    albums: albums.AlbumsResource
    artists: artists.ArtistsResource
    shows: shows.ShowsResource
    episodes: episodes.EpisodesResource
    audiobooks: audiobooks.AudiobooksResource
    me: me.MeResource
    chapters: chapters.ChaptersResource
    tracks: tracks.TracksResource
    search: search.SearchResource
    playlists: playlists.PlaylistsResource
    users: users.UsersResource
    browse: browse.BrowseResource
    audio_features: audio_features.AudioFeaturesResource
    audio_analysis: audio_analysis.AudioAnalysisResource
    recommendations: recommendations.RecommendationsResource
    markets: markets.MarketsResource
    with_raw_response: SpottedWithRawResponse
    with_streaming_response: SpottedWithStreamedResponse

    # client options
    client_id: str | None
    client_secret: str | None
    access_token: str | None

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
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
        """Construct a new synchronous Spotted client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `client_id` from `SPOTIFY_CLIENT_ID`
        - `client_secret` from `SPOTIFY_CLIENT_SECRET`
        - `access_token` from `SPOTIFY_ACCESS_TOKEN`
        """
        if client_id is None:
            client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_id = client_id

        if client_secret is None:
            client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self.client_secret = client_secret

        if access_token is None:
            access_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")
        self.access_token = access_token

        if base_url is None:
            base_url = os.environ.get("SPOTTED_BASE_URL")
        if base_url is None:
            base_url = f"https://api.spotify.com/v1"

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

        self.albums = albums.AlbumsResource(self)
        self.artists = artists.ArtistsResource(self)
        self.shows = shows.ShowsResource(self)
        self.episodes = episodes.EpisodesResource(self)
        self.audiobooks = audiobooks.AudiobooksResource(self)
        self.me = me.MeResource(self)
        self.chapters = chapters.ChaptersResource(self)
        self.tracks = tracks.TracksResource(self)
        self.search = search.SearchResource(self)
        self.playlists = playlists.PlaylistsResource(self)
        self.users = users.UsersResource(self)
        self.browse = browse.BrowseResource(self)
        self.audio_features = audio_features.AudioFeaturesResource(self)
        self.audio_analysis = audio_analysis.AudioAnalysisResource(self)
        self.recommendations = recommendations.RecommendationsResource(self)
        self.markets = markets.MarketsResource(self)
        self.with_raw_response = SpottedWithRawResponse(self)
        self.with_streaming_response = SpottedWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        access_token = self.access_token
        if access_token is None:
            return {}
        return {"Authorization": f"Bearer {access_token}"}

    @property
    @override
    def custom_auth(self) -> httpx.Auth | None:
        if self.client_id and self.client_secret:
            return make_oauth2(
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_url=self._prepare_url("https://accounts.spotify.com/api/token"),
                header="Authorization",
            )
        return None

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    @override
    def _should_retry(self, response: httpx.Response) -> bool:
        # Retry on 401 if we are using OAuth2 and the token might be expired
        if response.status_code == 401 and isinstance(self.custom_auth, OAuth2ClientCredentials):
            if self.custom_auth.token_is_expired():
                self.custom_auth.invalidate_token()
                return True
        return super()._should_retry(response)

    def copy(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
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
            client_id=client_id or self.client_id,
            client_secret=client_secret or self.client_secret,
            access_token=access_token or self.access_token,
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


class AsyncSpotted(AsyncAPIClient):
    albums: albums.AsyncAlbumsResource
    artists: artists.AsyncArtistsResource
    shows: shows.AsyncShowsResource
    episodes: episodes.AsyncEpisodesResource
    audiobooks: audiobooks.AsyncAudiobooksResource
    me: me.AsyncMeResource
    chapters: chapters.AsyncChaptersResource
    tracks: tracks.AsyncTracksResource
    search: search.AsyncSearchResource
    playlists: playlists.AsyncPlaylistsResource
    users: users.AsyncUsersResource
    browse: browse.AsyncBrowseResource
    audio_features: audio_features.AsyncAudioFeaturesResource
    audio_analysis: audio_analysis.AsyncAudioAnalysisResource
    recommendations: recommendations.AsyncRecommendationsResource
    markets: markets.AsyncMarketsResource
    with_raw_response: AsyncSpottedWithRawResponse
    with_streaming_response: AsyncSpottedWithStreamedResponse

    # client options
    client_id: str | None
    client_secret: str | None
    access_token: str | None

    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
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
        """Construct a new async AsyncSpotted client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `client_id` from `SPOTIFY_CLIENT_ID`
        - `client_secret` from `SPOTIFY_CLIENT_SECRET`
        - `access_token` from `SPOTIFY_ACCESS_TOKEN`
        """
        if client_id is None:
            client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        self.client_id = client_id

        if client_secret is None:
            client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        self.client_secret = client_secret

        if access_token is None:
            access_token = os.environ.get("SPOTIFY_ACCESS_TOKEN")
        self.access_token = access_token

        if base_url is None:
            base_url = os.environ.get("SPOTTED_BASE_URL")
        if base_url is None:
            base_url = f"https://api.spotify.com/v1"

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

        self.albums = albums.AsyncAlbumsResource(self)
        self.artists = artists.AsyncArtistsResource(self)
        self.shows = shows.AsyncShowsResource(self)
        self.episodes = episodes.AsyncEpisodesResource(self)
        self.audiobooks = audiobooks.AsyncAudiobooksResource(self)
        self.me = me.AsyncMeResource(self)
        self.chapters = chapters.AsyncChaptersResource(self)
        self.tracks = tracks.AsyncTracksResource(self)
        self.search = search.AsyncSearchResource(self)
        self.playlists = playlists.AsyncPlaylistsResource(self)
        self.users = users.AsyncUsersResource(self)
        self.browse = browse.AsyncBrowseResource(self)
        self.audio_features = audio_features.AsyncAudioFeaturesResource(self)
        self.audio_analysis = audio_analysis.AsyncAudioAnalysisResource(self)
        self.recommendations = recommendations.AsyncRecommendationsResource(self)
        self.markets = markets.AsyncMarketsResource(self)
        self.with_raw_response = AsyncSpottedWithRawResponse(self)
        self.with_streaming_response = AsyncSpottedWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        access_token = self.access_token
        if access_token is None:
            return {}
        return {"Authorization": f"Bearer {access_token}"}

    @property
    @override
    def custom_auth(self) -> httpx.Auth | None:
        if self.client_id and self.client_secret:
            return make_oauth2(
                client_id=self.client_id,
                client_secret=self.client_secret,
                token_url=self._prepare_url("https://accounts.spotify.com/api/token"),
                header="Authorization",
            )
        return None

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    @override
    def _should_retry(self, response: httpx.Response) -> bool:
        # Retry on 401 if we are using OAuth2 and the token might be expired
        if response.status_code == 401 and isinstance(self.custom_auth, OAuth2ClientCredentials):
            if self.custom_auth.token_is_expired():
                self.custom_auth.invalidate_token()
                return True
        return super()._should_retry(response)

    def copy(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
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
            client_id=client_id or self.client_id,
            client_secret=client_secret or self.client_secret,
            access_token=access_token or self.access_token,
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


class SpottedWithRawResponse:
    def __init__(self, client: Spotted) -> None:
        self.albums = albums.AlbumsResourceWithRawResponse(client.albums)
        self.artists = artists.ArtistsResourceWithRawResponse(client.artists)
        self.shows = shows.ShowsResourceWithRawResponse(client.shows)
        self.episodes = episodes.EpisodesResourceWithRawResponse(client.episodes)
        self.audiobooks = audiobooks.AudiobooksResourceWithRawResponse(client.audiobooks)
        self.me = me.MeResourceWithRawResponse(client.me)
        self.chapters = chapters.ChaptersResourceWithRawResponse(client.chapters)
        self.tracks = tracks.TracksResourceWithRawResponse(client.tracks)
        self.search = search.SearchResourceWithRawResponse(client.search)
        self.playlists = playlists.PlaylistsResourceWithRawResponse(client.playlists)
        self.users = users.UsersResourceWithRawResponse(client.users)
        self.browse = browse.BrowseResourceWithRawResponse(client.browse)
        self.audio_features = audio_features.AudioFeaturesResourceWithRawResponse(client.audio_features)
        self.audio_analysis = audio_analysis.AudioAnalysisResourceWithRawResponse(client.audio_analysis)
        self.recommendations = recommendations.RecommendationsResourceWithRawResponse(client.recommendations)
        self.markets = markets.MarketsResourceWithRawResponse(client.markets)


class AsyncSpottedWithRawResponse:
    def __init__(self, client: AsyncSpotted) -> None:
        self.albums = albums.AsyncAlbumsResourceWithRawResponse(client.albums)
        self.artists = artists.AsyncArtistsResourceWithRawResponse(client.artists)
        self.shows = shows.AsyncShowsResourceWithRawResponse(client.shows)
        self.episodes = episodes.AsyncEpisodesResourceWithRawResponse(client.episodes)
        self.audiobooks = audiobooks.AsyncAudiobooksResourceWithRawResponse(client.audiobooks)
        self.me = me.AsyncMeResourceWithRawResponse(client.me)
        self.chapters = chapters.AsyncChaptersResourceWithRawResponse(client.chapters)
        self.tracks = tracks.AsyncTracksResourceWithRawResponse(client.tracks)
        self.search = search.AsyncSearchResourceWithRawResponse(client.search)
        self.playlists = playlists.AsyncPlaylistsResourceWithRawResponse(client.playlists)
        self.users = users.AsyncUsersResourceWithRawResponse(client.users)
        self.browse = browse.AsyncBrowseResourceWithRawResponse(client.browse)
        self.audio_features = audio_features.AsyncAudioFeaturesResourceWithRawResponse(client.audio_features)
        self.audio_analysis = audio_analysis.AsyncAudioAnalysisResourceWithRawResponse(client.audio_analysis)
        self.recommendations = recommendations.AsyncRecommendationsResourceWithRawResponse(client.recommendations)
        self.markets = markets.AsyncMarketsResourceWithRawResponse(client.markets)


class SpottedWithStreamedResponse:
    def __init__(self, client: Spotted) -> None:
        self.albums = albums.AlbumsResourceWithStreamingResponse(client.albums)
        self.artists = artists.ArtistsResourceWithStreamingResponse(client.artists)
        self.shows = shows.ShowsResourceWithStreamingResponse(client.shows)
        self.episodes = episodes.EpisodesResourceWithStreamingResponse(client.episodes)
        self.audiobooks = audiobooks.AudiobooksResourceWithStreamingResponse(client.audiobooks)
        self.me = me.MeResourceWithStreamingResponse(client.me)
        self.chapters = chapters.ChaptersResourceWithStreamingResponse(client.chapters)
        self.tracks = tracks.TracksResourceWithStreamingResponse(client.tracks)
        self.search = search.SearchResourceWithStreamingResponse(client.search)
        self.playlists = playlists.PlaylistsResourceWithStreamingResponse(client.playlists)
        self.users = users.UsersResourceWithStreamingResponse(client.users)
        self.browse = browse.BrowseResourceWithStreamingResponse(client.browse)
        self.audio_features = audio_features.AudioFeaturesResourceWithStreamingResponse(client.audio_features)
        self.audio_analysis = audio_analysis.AudioAnalysisResourceWithStreamingResponse(client.audio_analysis)
        self.recommendations = recommendations.RecommendationsResourceWithStreamingResponse(client.recommendations)
        self.markets = markets.MarketsResourceWithStreamingResponse(client.markets)


class AsyncSpottedWithStreamedResponse:
    def __init__(self, client: AsyncSpotted) -> None:
        self.albums = albums.AsyncAlbumsResourceWithStreamingResponse(client.albums)
        self.artists = artists.AsyncArtistsResourceWithStreamingResponse(client.artists)
        self.shows = shows.AsyncShowsResourceWithStreamingResponse(client.shows)
        self.episodes = episodes.AsyncEpisodesResourceWithStreamingResponse(client.episodes)
        self.audiobooks = audiobooks.AsyncAudiobooksResourceWithStreamingResponse(client.audiobooks)
        self.me = me.AsyncMeResourceWithStreamingResponse(client.me)
        self.chapters = chapters.AsyncChaptersResourceWithStreamingResponse(client.chapters)
        self.tracks = tracks.AsyncTracksResourceWithStreamingResponse(client.tracks)
        self.search = search.AsyncSearchResourceWithStreamingResponse(client.search)
        self.playlists = playlists.AsyncPlaylistsResourceWithStreamingResponse(client.playlists)
        self.users = users.AsyncUsersResourceWithStreamingResponse(client.users)
        self.browse = browse.AsyncBrowseResourceWithStreamingResponse(client.browse)
        self.audio_features = audio_features.AsyncAudioFeaturesResourceWithStreamingResponse(client.audio_features)
        self.audio_analysis = audio_analysis.AsyncAudioAnalysisResourceWithStreamingResponse(client.audio_analysis)
        self.recommendations = recommendations.AsyncRecommendationsResourceWithStreamingResponse(client.recommendations)
        self.markets = markets.AsyncMarketsResourceWithStreamingResponse(client.markets)


Client = Spotted

AsyncClient = AsyncSpotted
