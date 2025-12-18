# xml-sanitizer

Safely escape illegal ampersands in XML without double-encoding.

## Why?

XML breaks if raw `&` exists:

- Jack & Tom : It will break
- Jack &amp; Tom : It works for xml without breaking

This library fixes that safely.

## Installation

```bash
pip install xml-sanitizer
```

## Usage

```python
from xml_sanitizer import xml_content_cleanup

parsed_xml = xml_content_cleanup(xml_file)

print(f"Cleaned XML: {parsed_xml}")
```
