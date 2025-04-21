# Blogspot Link Extractor

A simple Python script to extract all blog links from a Blogspot user’s profile and resolve any JavaScript-based redirects (e.g., `window.location` in `<script>` tags) to their final URLs.

## Features

- Fetches all blog links from a given Blogspot profile URL.
- Follows and extracts redirect URLs set via JavaScript (`window.location`).
- Outputs both the original and redirected URLs.
- Provides a summary of unique redirected links.

## Requirements

- Python 3.x
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python link_extract.py <blogspot_profile_url>
```

## Output

```text
<blogspot_profile_url> -> <redirected_url>
<blogspot_profile_url> -> <redirected_url>
...
Unique Redirecting Links:
<redirected_url>
<redirected_url>
...
```
