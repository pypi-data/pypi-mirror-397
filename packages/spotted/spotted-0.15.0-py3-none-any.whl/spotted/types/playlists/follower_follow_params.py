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

    published: bool
    """
    The playlist's public/private status (if it should be added to the user's
    profile or not): `true` the playlist will be public, `false` the playlist will
    be private, `null` the playlist status is not relevant. For more about
    public/private status, see
    [Working with Playlists](/documentation/web-api/concepts/playlists)
    """
