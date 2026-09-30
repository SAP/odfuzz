[![Build Status](https://travis-ci.com/SAP/odfuzz.svg?branch=master)](https://travis-ci.com/SAP/odfuzz)
[![codecov](https://codecov.io/gh/SAP/odfuzz/branch/master/graph/badge.svg)](https://codecov.io/gh/SAP/odfuzz)
[![REUSE status](https://api.reuse.software/badge/github.com/SAP/odfuzz)](https://api.reuse.software/info/github.com/SAP/odfuzz)


# odfuzz — OData URL generator

A Python library that generates random, valid OData V2 URLs and request bodies from a service metadata document. Useful for fuzz-testing OData services and for generating realistic test fixtures.

Example of generated URLs:

```
ValueHelpPrinters?$filter=Location eq '~' and Location eq '>'&sap-client=500&$format=json
C_PaymentAdvice?$top=869&$filter=IsActiveEntity eq false or CashDiscountAmountInPaytCrcy eq 1919771231157915484160m&sap-client=500&$format=json
C_Cpbupaemailvh?$top=81&$skip=245&sap-client=500&$format=json
SupportedChannelSet(Event='Ot',VariantId='V',CorrespondenceTypeId='M')?$filter=CorrespondenceTypeId ge 'ae' and CorrespondenceTypeId gt 'z'&sap-client=500&$format=json
```

## Requirements

- Python 3.9+

## Installation

```
pip install odfuzz
```

Or from source:

```
git clone https://github.com/SAP/odfuzz && cd odfuzz
pip install .
```

## Quick start

```python
from odfuzz.entities import DirectBuilder

# Read your OData service metadata XML
with open("metadata.xml", "rb") as f:
    metadata = f.read()

builder = DirectBuilder(metadata, method="GET")

# Generate 20 random GET URLs
results = builder.generate_n(20)
for r in results:
    print(r.url)
```

Each item in the list is a `QueryResult` dataclass:

```python
@dataclass
class QueryResult:
    url: str          # e.g. "Products?$filter=Price gt 10.0m&$top=50&sap-client=500"
    entity_set: str   # e.g. "Products"
    http_method: str  # e.g. "GET"
    body: dict | None # populated for PUT / POST / MERGE, empty dict for GET / DELETE
```

## API reference

### `DirectBuilder`

```python
DirectBuilder(
    metadata: bytes | str,
    restrictions=None,
    method: str = "GET",
    sap_vendor_enabled: bool = False,
    config=None,
)
```

| Parameter | Description |
|---|---|
| `metadata` | OData service metadata XML, as `bytes` (recommended) or `str`. |
| `restrictions` | A `RestrictionsGroup` instance, or `None` to apply no restrictions. |
| `method` | HTTP method to generate queries for: `"GET"`, `"DELETE"`, `"PUT"`, `"POST"`, or `"MERGE"`. |
| `sap_vendor_enabled` | Set `True` for SAP services that carry SAP-specific OData annotations (e.g. `sap:filterable`). Set `False` for standard OData services. |
| `config` | Optional `FuzzerConfig` instance for advanced configuration. When omitted, values are read from environment variables (see below). |

#### `build() → list`

Parse the metadata and return the list of queryable entity groups. Usually you call `generate_n()` directly instead.

#### `generate_n(n: int, seed: int | None = None) → list[QueryResult]`

Generate `n` query results. Pass `seed` to make the output reproducible:

```python
# Reproducible — same seed always produces the same URLs
results = builder.generate_n(10, seed=42)

# Verify two runs with the same seed are identical
builder_a = DirectBuilder(metadata, method="GET")
builder_b = DirectBuilder(metadata, method="GET")
assert [r.url for r in builder_a.generate_n(10, seed=42)] \
    == [r.url for r in builder_b.generate_n(10, seed=42)]
```

`seed` calls `random.seed()` which is process-global. Avoid calling `generate_n` concurrently with different seeds in the same process.

### `RestrictionsGroup`

Controls which entity sets, properties, and query options are included in generation. Accepts a YAML file path or a plain dict.

```python
from odfuzz.restrictions import RestrictionsGroup

# Exclude a property by name across all entity sets
exclusions = {"$ENTITY_SET$": {".*": {"Properties": ["SensitiveField"], "Nav_Properties": []}}}
restrictions = RestrictionsGroup(None, exclusions)

builder = DirectBuilder(metadata, restrictions=restrictions, method="GET")
```

See [`doc/restrictions.rst`](doc/restrictions.rst) for the full restriction syntax.

## Configuration

Runtime behaviour is controlled by environment variables:

| Variable | Default | Description |
|---|---|---|
| `ODFUZZ_SAP_CLIENT` | `500` | SAP client ID appended as `sap-client=` to every URL. Set to empty string to omit it. |
| `ODFUZZ_DATA_FORMAT` | `json` | Value appended as `$format=` to every GET URL (`json` or `xml`). |
| `ODFUZZ_USE_ENCODER` | `True` | URL-encode generated string values. Set to `False` to disable. Only affects `Edm.String` and `Edm.Double` properties, and the `search` query option. |
| `ODFUZZ_IGNORE_METADATA_RESTRICTIONS` | `False` | When `True`, metadata-level filter/sort restrictions are ignored and all properties are treated as filterable and sortable. |

## Supported query options

For `GET` requests, `generate_n` produces URLs with any combination of:

- `$filter` — property comparisons, logical operators, and OData functions (`substringof`, `startswith`, `endswith`, `year`, `round`, etc.)
- `$orderby`
- `$top`
- `$skip`
- `$expand`
- `search`
- `$inlinecount`

For `PUT` and `POST`, a JSON request body is generated alongside the URL. For `MERGE`, a partial body (random subset of non-key properties) is generated. `DELETE` generates key-predicate URLs with no body.

## Supported Edm types

`Edm.Binary`, `Edm.Boolean`, `Edm.Byte`, `Edm.DateTime`, `Edm.DateTimeOffset`, `Edm.Decimal`, `Edm.Double`, `Edm.Guid`, `Edm.Int16`, `Edm.Int32`, `Edm.Int64`, `Edm.Single`, `Edm.String`, `Edm.Time`

## Limitations

- OData V2 only.
- SAP-specific annotations (`sap:filterable`, `sap:sortable`, etc.) are respected when `sap_vendor_enabled=True`. Standard CSDL `Filterable`/`Sortable` attributes are respected when `sap_vendor_enabled=False`.
- `random.seed()` is process-global; do not call `generate_n` with different seeds concurrently in the same process.

## OData references

- [OData V2 URI conventions](https://www.odata.org/documentation/odata-version-2-0/uri-conventions/)
- [SAP OData annotations](https://wiki.scn.sap.com/wiki/display/EmTech/SAP+Annotations+for+OData+Version+2.0)

## Contributing

Use a single commit per logical change. Include a clear commit message explaining what changed and why. Open a pull request against `master`.

## License

Copyright (c) 2026 SAP SE or an SAP affiliate company. All rights reserved. This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the LICENSE file
