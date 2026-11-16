# Development Guide

## Repository Branches

- `main`: The main branch for stable releases.
- `dev`: The development branch for ongoing work.
- `store`: Special branch for Plugin Store release.
- ~~`external`: Branch for external importer source code.~~ (Deprecated)
- ~~`gh-pages`: Branch for external importer release.~~ (Deprecated)

## Plugin Structure

Based on Decky Loader architecture, Decky Clash consists of the following components:

```sh
~/homebrew
├── plugins
│   └── DeckyClash
│       ├── bin             # Dependency binaries
│       │   └── mihomo
│       ├── dist            # Decky frontend
│       │   ├── index.html
│       │   └── ...
│       ├── external        # External importer
│       │   ├── index.html
│       │   └── ...
│       ├── data            # Initial resources
│       │   └── ...
│       ├── py_modules      # Python modules
│       ├── main.py         # Plugin entrypoint
│       ├── override.yaml   # Override manifest
│       ├── package.json    # Package manifest
│       └── plugin.json     # Plugin metadata
├── data
│   └── DeckyClash
│       ├── dashboard       # Dashboards
│       │   ├── metacubexd
│       │   ├── yacd
│       │   ├── zashboard
│       │   └── ...         # Other dashboards
│       ├── ASN.mmdb        # Geo files (also below)
│       ├── BundleMRS.7z    # Bundled MRS rule sets
│       ├── GeoIP.dat
│       ├── GeoIP.metadb
│       └── GeoSite.dat
├── settings
│   └── DeckyClash
│       ├── subscriptions   # Subscription files
│       │   └── ...
│       └── config.json     # Settings
└── logs
    └── DeckyClash
        └── ...
```

## Settings Structure

The settings json file is located at `~/homebrew/settings/DeckyClash/config.json` by default.

```jsonc
{
  "subscriptions": {
    // Subscriptions Dictionary
    //   Key: Subscription Name
    //     (with .yaml extension is corresponding file name)
    //   Value: Subscription URL
    //     (supports http(s)://... and file://...)
    "Example": "file://example_url"
    // ~/homebrew/settings/DeckyClash/subscriptions/Example.yaml
  },
  "current": "Example",               // Current subscription. Default: [none]
  "dashboard": "yacd",                // Current dashboard. Default: [none]
  "secret": "RANDOM_SECRET",          // Controller secret. Default: [random]
  "override_dns": true,               // Override DNS settings. Default: true
  "enhanced_mode": "fake-ip",         // Enhanced mode. Default: fake-ip
  "controller_port": 9090,            // Controller port. Default: 9090
  "external_port": 50581,             // External importer port. Default: 50581
  "allow_remote_access": false,       // Allow remote access. Default: false
  "autostart": true,                  // Autostart after loaded. Default: false
  "timeout": 15.0,                    // Resource query timeout (s). Default: 15.0
  "user_agent_override": "",          // Override User-Agent. Default: [none]
  "subscription_hwid": "UUIDv4",     // Persistent X-Hwid for remote subscriptions. Default: [generated]
  "debounce_time": 10.0,              // Query debounce time (s). Default: 10.0
  "disable_verify": false,            // Disable verify SSL. Default: false
  "external_run_bg": false,           // Run external importer in background. Default: false
  "auto_check_update": true,          // Auto check update. Default: true
  "auto_update_subscription": false,  // Auto update subscription. Default: false
  "skip_steam_download": false,       // Skip proxy for Steam download. Default: false
  "log_level": "DEBUG"                // Log level. Default: INFO
}
```

`subscription_hwid` is generated once and reused for subscription imports and
updates. It is stored in the settings backup. Deleting the settings generates a
new identity; restoring a backup preserves the identity in that backup.

Subscription response headers are checked before saving a profile, including
responses with HTTP 200. `HWID_MAX_DEVICES_REACHED` is translated in the plugin and
external importer. Other HWID refusals are logged and return the generic
`SUBSCRIPTION_REQUEST_FAILED` message; an existing profile is preserved.

## Build and release

GitHub Actions builds archives for pull requests and pushes to `main` or `dev`.
Pushing a `v` tag (for example, `v1.0.0`) builds and publishes a GitHub Release with
these four release assets:

- `DeckyClash.zip`: small plugin package (about 4 MB), with resources downloaded
  through the installation guide after installation.
- `DeckyClash-full-linux-amd64.zip`: plugin, amd64 Mihomo executable, dashboards,
  and Geo files for Steam Deck and other x86-64 devices.
- `DeckyClash-full-linux-arm64.zip`: the corresponding full package for ARM64
  devices only.
- `version.txt`: the published version used by update checks.

All three ZIPs use the same `DeckyClash/` plugin directory layout and can be
installed through Decky Settings → Developer. For **Install Plugin from ZIP
File**, download or copy the ZIP onto the target device first, then select it
with **Browse**. **Install Plugin from URL** downloads the selected release asset
over the internet. Full packages carry the resource files in the plugin's
`data/` directory; `initialize_plugin()` imports them on first load. The separate
small `install.sh` online installer remains available as an additional method.

Pushing to `dev` publishes the `nightly` prerelease. Enable Actions in the fork
before using these workflows.

Run the subscription regression tests locally with:

```sh
python3 -m unittest discover -s tests -v
```
