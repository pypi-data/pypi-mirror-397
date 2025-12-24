# Safari Cloud Tabs

Safari Cloud Tabs is a command-line tool to manage and open Safari iCloud tabs
from other devices. It allows you to list, filter, and open tabs synchronized
via iCloud on macOS.

## Installation

### Requirements

- macOS
- Python 3.9 or newer
- Safari with iCloud Tabs enabled

### Install from PyPI

```bash
pip install safari-cloud-tabs
```

### Install from GitHub

```bash
pip install git+https://github.com/osantana/safari-cloud-tabs.git
```

## Usage

### Basic commands

List all devices with iCloud tabs:

```bash
safari-cloud-tabs --list-devices
```

Open all tabs from all devices in the default browser:

```bash
safari-cloud-tabs
```

Show all tabs without opening them (dry run):

```bash
safari-cloud-tabs --dry-run
```

### Filtering

Filter tabs by device name:

```bash
safari-cloud-tabs --device "iPhone"
```

Filter tabs by URL content:

```bash
safari-cloud-tabs --contains "github.com"
```

Limit the number of tabs to open:

```bash
safari-cloud-tabs --limit 5
```

### Browser selection

Open tabs in a specific browser (safari, chrome, or firefox):

```bash
safari-cloud-tabs --browser chrome
```

### Other options

Open in the current tab instead of a new tab:

```bash
safari-cloud-tabs --no-new-tab
```

Set a delay between opening tabs:

```bash
safari-cloud-tabs --delay 0.5
```

## Development

To contribute to the development of Safari Cloud Tabs:

1. Clone the repository:
   ```bash
   git clone https://github.com/osantana/safari-cloud-tabs.git
   cd safari-cloud-tabs
   ```

2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

3. Make your changes and verify them.

4. Submit a Pull Request.

### Publishing to PyPI

To publish a new version to PyPI:

1. Build the package:
   ```bash
   uv build
   ```

2. Publish the package:
   ```bash
   uv publish
   ```

Note: `uv` does not automatically read your `~/.pypirc` file. You can provide
the API token using the `UV_PUBLISH_TOKEN` environment variable or the `--token`
argument:

```bash
# Using an environment variable
export UV_PUBLISH_TOKEN=your-pypi-api-token
uv publish

# Or passing the token directly
uv publish --token YOUR_PYPI_API_TOKEN
```
