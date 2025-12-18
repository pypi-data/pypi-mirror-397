# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ..._types import SequenceNotStr

__all__ = ["EpisodeRemoveParams"]


class EpisodeRemoveParams(TypedDict, total=False):
    ids: SequenceNotStr[str]
    """
    A JSON array of the
    [Spotify IDs](/documentation/web-api/concepts/spotify-uris-ids). <br/>A maximum
    of 50 items can be specified in one request. _**Note**: if the `ids` parameter
    is present in the query string, any IDs listed here in the body will be
    ignored._
    """
