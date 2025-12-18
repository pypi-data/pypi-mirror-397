# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..._types import SequenceNotStr

__all__ = ["ShowSaveParams"]


class ShowSaveParams(TypedDict, total=False):
    ids: SequenceNotStr[str]
    """
    A JSON array of the
    [Spotify IDs](https://developer.spotify.com/documentation/web-api/#spotify-uris-and-ids).
    A maximum of 50 items can be specified in one request. _Note: if the `ids`
    parameter is present in the query string, any IDs listed here in the body will
    be ignored._
    """
