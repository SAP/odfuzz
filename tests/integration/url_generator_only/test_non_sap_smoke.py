"""Smoke tests for DirectBuilder with plain (non-SAP) OData V2 metadata."""

from pathlib import Path

import pytest

from odfuzz.entities import DirectBuilder
from odfuzz.fuzzer import QueryResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plain_metadata() -> bytes:
    path = Path(__file__).parent / "metadata-plain-odata-v2.xml"
    return path.read_bytes()


# ---------------------------------------------------------------------------
# Task A: Smoke test for non-SAP metadata
# ---------------------------------------------------------------------------

def test_generate_n_returns_correct_count():
    """generate_n(5) should return exactly 5 QueryResult objects."""
    metadata = _plain_metadata()
    builder = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results = builder.generate_n(5)

    assert len(results) == 5


def test_generate_n_items_are_query_results():
    """Every item returned by generate_n should be a QueryResult instance."""
    metadata = _plain_metadata()
    builder = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results = builder.generate_n(5)

    for item in results:
        assert isinstance(item, QueryResult), f"Expected QueryResult, got {type(item)}"


def test_generate_n_url_is_non_empty_string():
    """Every QueryResult.url should be a non-empty string."""
    metadata = _plain_metadata()
    builder = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results = builder.generate_n(5)

    for item in results:
        assert isinstance(item.url, str), f"url should be str, got {type(item.url)}"
        assert item.url != "", "url must not be empty"


def test_generate_n_entity_set_is_products():
    """Every QueryResult.entity_set should equal 'Products'."""
    metadata = _plain_metadata()
    builder = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results = builder.generate_n(5)

    for item in results:
        assert item.entity_set == "Products", (
            f"Expected entity_set='Products', got '{item.entity_set}'"
        )


def test_generate_n_http_method_is_get():
    """Every QueryResult.http_method should equal 'GET'."""
    metadata = _plain_metadata()
    builder = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results = builder.generate_n(5)

    for item in results:
        assert item.http_method == "GET", (
            f"Expected http_method='GET', got '{item.http_method}'"
        )


def test_generate_n_result_has_required_attributes():
    """Each QueryResult must expose url, entity_set, http_method, and body."""
    metadata = _plain_metadata()
    builder = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results = builder.generate_n(5)

    for item in results:
        assert hasattr(item, "url")
        assert hasattr(item, "entity_set")
        assert hasattr(item, "http_method")
        assert hasattr(item, "body")


# ---------------------------------------------------------------------------
# Task B: Deterministic generation (seed-based) — placeholder until FR-2
# ---------------------------------------------------------------------------

def test_deterministic_generation_with_seed():
    """generate_n(10, seed=42) called twice must return identical URL lists."""
    metadata = _plain_metadata()

    builder_a = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results_a = builder_a.generate_n(10, seed=42)

    builder_b = DirectBuilder(metadata, restrictions=None, method="GET", sap_vendor_enabled=False)
    results_b = builder_b.generate_n(10, seed=42)

    assert [r.url for r in results_a] == [r.url for r in results_b]
