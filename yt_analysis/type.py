from typing import TypedDict, Literal, Any, Iterable, Required


class _InfoDict(TypedDict, total=False):
    age_limit: int
    availability: Literal["private", "premium_only",
                          "subscriber_only", "needs_auth", "unlisted", "public"] | None
    available_at: int
    creator: str | None
    comment_count: int | None
    duration: int | None
    formats: list[dict[str, Any]] | None
    id: Required[str]
    like_count: int | None
    tags: list[str] | None
    thumbnail: str | None
    timestamp: int | float | None
    title: str | None
    uploader: str | None
    url: str | None
    requested_formats: Iterable["_InfoDict"]
