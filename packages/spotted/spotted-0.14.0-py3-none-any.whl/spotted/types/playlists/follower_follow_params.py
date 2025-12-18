# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["FollowerFollowParams"]


class FollowerFollowParams(TypedDict, total=False):
    public: bool
    """Defaults to `true`.

    If `true` the playlist will be included in user's public playlists (added to
    profile), if `false` it will remain private. For more about public/private
    status, see [Working with Playlists](/documentation/web-api/concepts/playlists)
    """
