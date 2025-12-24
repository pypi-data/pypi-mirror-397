# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["AccountListParams"]


class AccountListParams(TypedDict, total=False):
    country_codes: str
    """Filter by country codes.

    Comma-separated list of ISO 3166-1 alpha-2 codes (e.g., 'US,RU,GB').
    """

    page: int
    """Page number."""

    page_size: int
    """Number of items per page."""

    sort: Literal["price_asc", "price_desc", "name_asc", "name_desc"]
    """Sort order for accounts."""
