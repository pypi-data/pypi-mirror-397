# Ninja Zip Streamer

Streams a remote zip file without using the filesystem cache.

## Installation

The package can be installed using `pip`:

```
pip install ninja-zip-streamer
```

## Usage

Use `extract()` to simply pick files to extract:

```python
from ninja_zip_streamer import extract
extract(file_or_url, out_dir="/tmp")
```

Note that `extract()` returns the list of local extracted files.

### Suffixes

One can ask for specific suffixes to be extracted only;

```python
extract(file_or_url, out_dir="/tmp", only_suffixes=[".txt", "_o.bin"])
```

### Remote archive arguments

For remote archives you can provide `session` (a `request.Session`), `headers`, `verify` 
and `timeout` that are all optional parameters. Defaults are reasonably initialized :D

Example with headers:

```python
extract("https://site.org/toto.zip", out_dir="/tmp", headers={"X-API-Key": "4jtb...yvR"})
```

## Contact

- remi cresson @ inrae

