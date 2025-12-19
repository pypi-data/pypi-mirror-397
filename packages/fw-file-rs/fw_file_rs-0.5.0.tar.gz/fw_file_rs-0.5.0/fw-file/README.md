# fw-file-rs

A Rust library for reading, parsing, and de-identifying DICOM files
with bindings for Python and JavaScript/WebAssembly.

## Features

- **DICOM Metadata Extraction**: Extract specific DICOM tags from files efficiently
- **DICOM Grouping**: Group DICOM files by metadata tags with localizer detection
- **DICOM De-identification**: Comprehensive de-identification using YAML profiles
- **Cross-platform**: Available as Rust library, Python package, and JavaScript/WASM module

## De-identification Profile Features

The library supports comprehensive DICOM de-identification through YAML configuration profiles.

### Profile Structure

```yaml
version: 1
name: "Profile Name"
dicom:
  # Global options
  file-filter: "*.dcm"                # Single pattern or ["*.dcm", "*.tiff"] for multiple
  filenames:                          # Filename renaming rules
    - input-regex: '^(?P<prefix>\w+)-(?P<date>\d{4}-\d{2}-\d{2})\.dcm$'
      output: '{SOPInstanceUID}_{date}.dcm'
    - input-regex: '^(?P<uid>[\w.]+)-(?P<datetime>[\d\s:-]+)\.dcm$'
      output: '{uid}_{PatientID}.dcm'
  date-increment: 30                  # Days to shift all dates
  date-format: "%Y%m%d"               # Default format for parsing dates (increment-date)
  datetime-format: "%Y%m%d%H%M%S.%f"  # Default format for parsing datetimes (increment-datetime)
  datetime-min: "19900101"            # Global minimum date constraint (YYYYMMDD or relative)
  datetime-max: "20501231"            # Global maximum date constraint (YYYYMMDD or relative)
  jitter-date: false                  # Add random jitter to date operations
  jitter-unit: "days"                 # Unit for date jitter: "days", "weeks", or "years"
  jitter-type: "float"                # "float" or "int" for numeric jitter
  jitter-range: 2.0                   # Range for jittering values
  patient-age-from-birthdate: true    # Calculate age from birth/study dates
  patient-age-units: "Y"              # "Y", "M", or "D" for years/months/days
  recurse-sequence: false             # Apply actions to nested sequences
  remove-private-tags: true           # Remove all private tags
  remove-undefined: false             # Remove tags not explicitly defined
  replace-with-insert: true           # Insert tags if not exist
  uid-prefix-fields: 4                # Number of prefix fields to preserve/replace in UIDs
  uid-suffix-fields: 1                # Number of suffix fields to preserve in UIDs
  uid-numeric-name: "1.2.826.0.1"     # Registered OID to use as UID prefix
  salt: "salt-key"                    # Salt for hashing UIDs

  # Field-specific transformations
  fields:
    - name: "PatientName"             # Tag name, hex, or (group,element)
      replace-with: "REDACTED"        # Replace with static value
      replace-with-insert: false      # Field-level override: only replace if tag exists
    - name: "PatientID"
      remove: true                    # Remove tag completely
    - name: "StudyInstanceUID"
      hashuid: true                   # Hash UID maintaining structure
    - name: "PatientBirthDate"
      increment-date: true            # Apply date-increment
    - name: "PatientWeight"
      jitter: true                    # Add random noise
      jitter-range: 5.0               # Override global jitter range
      jitter-min: 40.0                # Minimum value after jittering
      jitter-max: 200.0               # Maximum value after jittering
    - regex: ".*Date.*"               # Use regex to match multiple tags
      increment-date: true
    - name: "(0031, \"AGFA PACS Archive Mirroring 1.0\", 01)"  # Private tags
      replace-with: "MODIFIED"
```

### Field Identification Methods

1. **Tag Names**: `"PatientName"`, `"StudyDate"`
2. **Hex Format**: `"00100010"`, `"0x00100010"`
3. **Tuple Format**: `"(0010, 0010)"`, `"(0008, 0020)"`
4. **Private Tags**: `"(group, \"creator\", element)"` format
5. **Repeater Tags**: `"(60xx, 0022)"`, `"50xx0010"` - Use `x` or `X` as wildcards
6. **Regex Patterns**: Match multiple tags with regular expressions

### Transformation Actions

#### replace-with

Replace tag value with a static string. Validates against DICOM VR constraints.

```yaml
- name: "PatientName"
  replace-with: "ANONYMOUS"
```

#### remove

Completely remove the tag from the DICOM file.

```yaml
- name: "PatientComments"
  remove: true
```

#### hash

Apply SHA-256 hash and truncate to 16 characters for anonymization.

```yaml
- name: "PatientID"
  hash: true
```

#### hashuid

Hash UIDs while preserving DICOM UID structure and length constraints.

```yaml
- name: "StudyInstanceUID"
  hashuid: true
```

#### increment-date

Shift dates by a specified number of days (uses global `date-increment`).
Use `date-format` for custom input parsing.

```yaml
- name: "StudyDate"
  increment-date: true
  date-format: "%Y-%m-%d"          # Optional: custom format for parsing input
  date-increment-override: 10      # Optional: override global date-increment
  datetime-min: "20000101"         # Optional: minimum date constraint
  datetime-max: "20501231"         # Optional: maximum date constraint
  jitter-date: true                # Optional: add random jitter to dates
  jitter-range: 5                  # Optional: jitter range in days
  jitter-unit: "days"              # Optional: "days", "weeks", or "years"
```

**Format Behavior:**

- For **DA (Date) fields**: Custom format used for parsing, output always uses
  DICOM standard `YYYYMMDD`
- For **text fields** (LO, SH, etc.): Custom format used for both parsing and
  output

**Date Constraints:**

- `datetime-min`/`datetime-max`: Fixed dates in `YYYYMMDD` format or relative
  (e.g., `"-1years"`, `"+30days"`)
- Field-level constraints override global constraints
- Dates are clamped to stay within min/max bounds after incrementing

#### increment-datetime

Shift datetime values with time component (uses global `date-increment`).
Use `datetime-format` for custom input parsing.

```yaml
- name: "AcquisitionDateTime"
  increment-datetime: true
  datetime-format: "%Y-%m-%d %H:%M:%S"  # Optional: custom format for parsing
  date-increment-override: 5            # Optional: override global date-increment
  datetime-min: "20000101"              # Optional: minimum datetime constraint
  datetime-max: "20501231"              # Optional: maximum datetime constraint
  jitter-date: true                     # Optional: add random jitter to datetimes
  jitter-range: 5                       # Optional: jitter range in days
  jitter-unit: "days"                   # Optional: "days", "weeks", or "years"
```

**Format Behavior:**

- For **DT (DateTime) fields**: Custom format used for parsing, output always
  uses DICOM standard `YYYYMMDDHHMMSS.ffffff`
- For **text fields** (LO, SH, etc.): Custom format used for both parsing and
  output

**Date Constraints:**

- `datetime-min`/`datetime-max`: Fixed dates in `YYYYMMDD` format or relative
  (e.g., `"-1years"`, `"+30days"`)
- Field-level constraints override global constraints
- Datetimes are clamped to stay within min/max bounds after incrementing
- Jitter is applied before min/max clamping

#### jitter

Add controlled random noise to numeric values.

```yaml
- name: "PatientWeight"
  jitter: true
  jitter-type: "float"      # or "int"
  jitter-range: 5.0         # ±5 units
  jitter-min: 40.0          # Minimum allowed value
  jitter-max: 200.0         # Maximum allowed value
```

### Global Options

- **file-filter**: Control which files the profile will process using Unix glob patterns
  - Can be a single pattern string: `"*.dcm"`
  - Or an array of patterns: `["*.dcm", "*.tiff", "*.tif"]`
  - Supports wildcards: `*` (matches everything), `?` (single character),
  `[seq]` (character class), `[!seq]` (negated class)
  - Matches against filename only, not full path
  - When not specified, all files match (no filtering)
  - Patterns are case-sensitive
- **date-increment**: Number of days to shift all dates
- **jitter-type**: Default jittering type (`"float"` or `"int"`)
- **jitter-range**: Default range for jittering operations
- **patient-age-from-birthdate**: Auto-calculate patient age from birth date and study date
- **patient-age-units**: Preferred units for patient age (`"Y"`, `"M"`, `"D"`)
- **recurse-sequence**: Apply field rules to nested DICOM sequences
- **remove-private-tags**: Remove all private tags (except those explicitly defined in fields)
- **remove-undefined**: Remove all tags except those explicitly defined in the profile

### Advanced Features

#### Sequence Recursion

Process nested DICOM sequences by setting `recurse-sequence: true`:

```yaml
dicom:
  recurse-sequence: true
  fields:
    - name: "StudyInstanceUID"
      hashuid: true  # Applied to all StudyInstanceUID tags in sequences too
```

#### Private Tag Support

Handle private DICOM tags with creator identification:

```yaml
fields:
  - name: "(2005, \"Philips MR Imaging DD 001\", 70)"
    replace-with: "REDACTED"
```

#### Regex Field Matching

Use regular expressions to match multiple related tags:

```yaml
fields:
  - regex: ".*Date.*"           # Match StudyDate, SeriesDate, etc.
    increment-date: true
  - regex: ".*InstanceUID.*"    # Match all UID tags
    hashuid: true
```

#### Repeater Tag Support

Handle DICOM repeater tags that use wildcards for group/element matching:

```yaml
fields:
  - name: "(60xx, 0022)"        # Matches (6000,0022), (6002,0022), (6004,0022), etc.
    replace-with: "REDACTED"
  - name: "50xx0010"
    remove: true
```

**Supported Patterns:**

- `(60xx, element)` - Wildcard in group for tuple format
- `50xx0010` - Wildcard in group for hex format
- `0x50xx0010` - Hex prefix with wildcards
- Wildcards only supported for groups 5xxx and 6xxx (overlay/curve repeating groups)

#### Patient Age Calculation

Automatically calculate and set patient age from birth date and study/series dates:

```yaml
dicom:
  patient-age-from-birthdate: true
  patient-age-units: "Y"        # Prefer years, fallback to months/days
  fields:
    - name: "PatientBirthDate"
      remove: true              # Remove after calculating age
```

#### Filename Renaming

Define rules to rename files during de-identification using regex patterns
and template substitution:

```yaml
dicom:
  filenames:
    - input-regex: '^(?P<prefix>\w+)-(?P<date>\d{4}-\d{2}-\d{2})\.dcm$'
      output: '{SOPInstanceUID}_{date}.dcm'
    - input-regex: '^(?P<uid>[\w.]+)-(?P<datetime>[\d\s:-]+)\.dcm$'
      output: '{uid}_{PatientID}.dcm'
```

**How It Works:**

1. **Input Matching**: Each rule's `input-regex` is tested against the filename
2. **First Match Wins**: Rules are evaluated in order; the first matching rule is used
3. **Template Substitution**: The `output` template supports two types of variables:
   - **Regex Captures**: Named groups from `input-regex` (e.g., `{date}`, `{prefix}`)
   - **DICOM Tags**: Any DICOM tag name (e.g., `{SOPInstanceUID}`, `{PatientID}`)

Using the example above, a file named `acquisition-2020-02-20.dcm` with
`SOPInstanceUID: 1.2.3.4.5.6.7.8.9` would be renamed to `1.2.3.4.5.6.7.8.9_2020-02-20.dcm`.

## Development

```bash
# run all tests and build
just
# list all available commands
just --list
```
