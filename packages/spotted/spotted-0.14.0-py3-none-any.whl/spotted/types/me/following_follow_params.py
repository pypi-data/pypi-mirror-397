# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["FollowingFollowParams"]


class FollowingFollowParams(TypedDict, total=False):
    ids: Required[SequenceNotStr[str]]
    """
    A JSON array of the artist or user
    [Spotify IDs](/documentation/web-api/concepts/spotify-uris-ids). For example:
    `{ids:["74ASZWbe4lXaubB36ztrGX", "08td7MxkoHQkXnWAYD8d6Q"]}`. A maximum of 50
    IDs can be sent in one request. _**Note**: if the `ids` parameter is present in
    the query string, any IDs listed here in the body will be ignored._
    """
