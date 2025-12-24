# Semantic Version GIT Tagger

A pretty trivial python script to easily manage git tags with semantic versioning (semver.org)  

## Usage

```bash
semtag [options]
```

### Options

<!-- OPTIONS:START -->
```
  -h, --help         show this help message and exit
  -v, --verbose      Verbosity (-v for INFO, -vv for DEBUG)
  -b, --by BY        Increment by a specific number
  -p, --patch        Increment patch version (x.x.PATCH)
  -m, --minor        Increment minor version (x.MINOR.0)
  -M, --major        Increment major version (MAJOR.0.0)
  -l, --label LABEL  Add label to the version (e.g., -l rc1 creates 1.0.0-rc1)
  -a, --msg MSG      Annotated tags message
  -u, --push         Push the new tag to remote repository
  -U, --pushall      Push all local tags to remote repository
  -n, --no-fetch     Do not fetch tags from remote before operation
```
<!-- OPTIONS:END -->

### Examples

```bash
# Increment minor version (1.0.0 -> 1.1.0)
semtag -m

# Increment major version (1.0.0 -> 2.0.0)
semtag -M

# Increment patch version (1.0.0 -> 1.0.5)
semtag -p -b 5

# Increment patch and add label (1.0.0 -> 1.0.1-rc1), don't fetch and push new tag
semtag -n -u -p -l rc1
```

## Installation

Using pip  (preferred)
```bash
pip install semtag
```

From git
```bash
git clone https://github.com/mateuszmikrut/semtag.git
cd semtag
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python ./semtag.py
```

## Supported Version Formats

The script supports semantic versioning with the following formats:
- `v1.0.0` (with 'v' prefix)
- `1.0.0` (without prefix)
- `1.0.0-rc1` (with prerelease label)

When incrementing versions, prerelease labels are automatically removed.

