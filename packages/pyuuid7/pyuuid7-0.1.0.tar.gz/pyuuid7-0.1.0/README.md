# PyUUID7

Fast UUID v4, v5, and v7 generation in Rust for Python.

## Installation

```bash
pip install pyuuid7
```

## Usage

```python
import pyuuid7

# Generate UUIDs
uuid_v4 = pyuuid7.uuid4()          # Random UUID
uuid_v7 = pyuuid7.uuid7()          # Time-sortable UUID
uuid_v5 = pyuuid7.uuid5(           # Name-based UUID
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "example.com"
)

# Validation and parsing
pyuuid7.is_valid("a1b2c3d4-...")   # True/False
pyuuid7.get_version("a1b2c3d4-...") # 4, 5, 7, etc.
pyuuid7.parse("A1B2C3D4-...")      # Lowercase canonical format
```

## UUID Versions

| Version | Description |
|---------|-------------|
| v4 | Random UUID (122 random bits) |
| v5 | Name-based UUID using SHA-1 |
| v7 | Time-sortable UUID (Unix timestamp + random) |

## Development

```bash
# Setup environment
mise install
mise run setup

# Build and test
mise run dev
mise run test
```

## License

MIT
