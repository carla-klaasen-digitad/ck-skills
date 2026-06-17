---
name: data-processor
description: Process, transform, and validate data files (CSV, JSON, YAML). Use when working with data files, data transformation, or when user mentions data processing, CSV, JSON, or data validation.
allowed-tools: Read, Write, Edit, Bash
---

# Data Processor

Processes data files (CSV, JSON, YAML), validates schemas, transforms data, and generates outputs.

## When This Skill Activates

- User asks to "process this data", "transform CSV", "convert JSON to YAML"
- User mentions "data processing", "data transformation", "file conversion"
- User needs to work with structured data files

## Data Processing Workflow

### Step 1: Understand the Data

Ask the user:
- **Input format**: CSV, JSON, YAML, Excel, XML?
- **Output format**: What should the result be?
- **Transformation**: What needs to change?
- **File size**: Small (< 1MB) or large (> 1GB)?

### Step 2: Read Input Data

#### CSV Files
```python
import csv
from pathlib import Path

def read_csv(file_path: Path) -> list[dict]:
    """Read CSV file and return list of dictionaries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Usage
data = read_csv(Path("input.csv"))
print(f"Read {len(data)} rows")
```

#### JSON Files
```python
import json
from pathlib import Path

def read_json(file_path: Path) -> dict | list:
    """Read JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Usage
data = read_json(Path("input.json"))
```

#### YAML Files
```python
import yaml
from pathlib import Path

def read_yaml(file_path: Path) -> dict | list:
    """Read YAML file (requires PyYAML)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# Usage
data = read_yaml(Path("input.yaml"))
```

### Step 3: Validate Schema

Define and validate against a schema:

```python
from typing import Any

def validate_row(row: dict, required_fields: list[str]) -> bool:
    """Validate that row has all required fields."""
    missing = [field for field in required_fields if field not in row or not row[field]]
    if missing:
        print(f"Missing required fields: {missing}")
        return False
    return True

# Validate all rows
required_fields = ["name", "email", "age"]
valid_rows = [row for row in data if validate_row(row, required_fields)]
print(f"Valid rows: {len(valid_rows)}/{len(data)}")
```

### Step 4: Transform Data

Common transformations:

#### Filter Data
```python
# Filter by condition
filtered = [row for row in data if int(row.get("age", 0)) > 18]

# Filter by multiple conditions
filtered = [
    row for row in data
    if row.get("status") == "active" and int(row.get("score", 0)) > 50
]
```

#### Map/Transform Fields
```python
def transform_row(row: dict) -> dict:
    """Transform a single row."""
    return {
        "fullName": f"{row['first_name']} {row['last_name']}",
        "emailAddress": row["email"].lower().strip(),
        "age": int(row["age"]),
    }

transformed = [transform_row(row) for row in data]
```

#### Aggregate Data
```python
from collections import Counter

# Count occurrences
counts = Counter(row["category"] for row in data)

# Sum by field
from collections import defaultdict
sums = defaultdict(int)
for row in data:
    sums[row["category"]] += float(row.get("amount", 0))

# Group by field
from itertools import groupby
sorted_data = sorted(data, key=lambda x: x["category"])
grouped = {k: list(g) for k, g in groupby(sorted_data, key=lambda x: x["category"])}
```

#### Sort Data
```python
# Sort by single field
sorted_data = sorted(data, key=lambda x: x.get("name", ""))

# Sort by multiple fields
sorted_data = sorted(data, key=lambda x: (x.get("category", ""), x.get("date", "")))

# Sort numeric descending
sorted_data = sorted(data, key=lambda x: float(x.get("score", 0)), reverse=True)
```

### Step 5: Write Output

#### Write CSV
```python
def write_csv(data: list[dict], file_path: Path) -> None:
    """Write data to CSV file."""
    if not data:
        print("No data to write")
        return

    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"Wrote {len(data)} rows to {file_path}")

# Usage
write_csv(transformed, Path("output.csv"))
```

#### Write JSON
```python
def write_json(data: dict | list, file_path: Path, indent: int = 2) -> None:
    """Write data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    print(f"Wrote JSON to {file_path}")

# Usage
write_json(transformed, Path("output.json"))
```

#### Write YAML
```python
def write_yaml(data: dict | list, file_path: Path) -> None:
    """Write data to YAML file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    print(f"Wrote YAML to {file_path}")

# Usage
write_yaml(transformed, Path("output.yaml"))
```

### Step 6: Handle Large Files

For files > 1GB, use streaming:

```python
# Process CSV in chunks
def process_large_csv(input_path: Path, output_path: Path, chunk_size: int = 10000):
    """Process large CSV file in chunks."""
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        writer = None
        processed = 0

        for i, row in enumerate(reader):
            # Transform row
            transformed = transform_row(row)

            # Initialize writer with headers
            if writer is None:
                writer = csv.DictWriter(outfile, fieldnames=transformed.keys())
                writer.writeheader()

            writer.writerow(transformed)
            processed += 1

            # Progress update
            if processed % chunk_size == 0:
                print(f"Processed {processed} rows...")

    print(f"Complete! Processed {processed} rows")
```

## Error Handling

```python
def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# Usage in transformations
transformed = [
    {
        "age": safe_int(row.get("age"), 0),
        "score": safe_float(row.get("score"), 0.0),
    }
    for row in data
]
```

## Examples

See [examples.md](examples.md) for complete data processing workflows.

## Troubleshooting

### Encoding Errors
- Try different encodings: `utf-8`, `latin-1`, `cp1252`
- Use `encoding='utf-8-sig'` for files with BOM
- Handle encoding errors: `errors='replace'` or `errors='ignore'`

### Missing Data
- Use `.get()` with defaults instead of direct access
- Validate required fields before processing
- Log or report rows with missing critical fields

### Memory Issues
- Process files in chunks for large datasets
- Use generators instead of lists where possible
- Write output incrementally instead of accumulating in memory

### Type Conversion Errors
- Use safe conversion functions (see above)
- Validate data types before operations
- Log unexpected values for debugging
