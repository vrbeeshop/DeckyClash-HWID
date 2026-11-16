# Development Guide

[Русский](./DEV_GUIDE.md) | **English** · [README](../README_EN.md) · [FAQ](./FAQ_EN.md)

## Repository branches

- `main`: the stable development branch of this fork.
- `dev`: an optional development branch supported by the workflow for the `nightly` prerelease; it has not been created in this fork.

Release and update URLs point to `vrbeeshop/DeckyClash-HWID`. This fork publishes ZIP packages through GitHub Releases.

## Plugin structure

Decky Loader keeps the plugin, runtime resources, settings, and logs in separate directories. The default installation layout is:

```text
~/homebrew
├── plugins
│   └── DeckyClash
│       ├── bin
│       │   └── mihomo           # Core executable for the target architecture
│       ├── dist
│       │   ├── index.js         # Built Decky frontend
│       │   └── index.js.map
│       ├── external             # External subscription importer
│       │   ├── index.html
│       │   ├── app.js
│       │   └── ...
│       ├── data                 # Initial resources in full ZIPs; removed after import
│       │   └── ...
│       ├── py_modules           # Python modules and bundled YAML library
│       ├── main.py              # Plugin entry point
│       ├── override.yaml        # Configuration overrides
│       ├── package.json
│       ├── plugin.json
│       └── LICENSE
├── data
│   └── DeckyClash
│       ├── dashboard
│       │   ├── metacubexd
│       │   ├── yacd
│       │   ├── zashboard
│       │   └── ...              # Other dashboards
│       ├── ASN.mmdb
│       ├── BundleMRS.7z
│       ├── GeoIP.dat
│       ├── GeoIP.metadb
│       ├── GeoSite.dat
│       └── running_config.yaml  # Generated configuration used by Mihomo
├── settings
│   └── DeckyClash
│       ├── subscriptions
│       │   └── Example.yaml
│       └── config.json
└── logs
    └── DeckyClash
        ├── core.log             # Mihomo output
        └── ...                  # Plugin logs
```

The small package does not include Mihomo or the initial resource directory. The plugin's installation guide downloads them. Full packages include `bin/mihomo` and `data/`. On first load, `initialize_plugin()` restores executable permissions in `bin`, copies bundled `data/` into the runtime directory, and removes the imported copy from the plugin directory.

The source directory `defaults/` supplies `external/` and `override.yaml` directly to the plugin package; the installed plugin does not need a `defaults/` directory.

## Settings structure

Settings are stored in `~/homebrew/settings/DeckyClash/config.json` by default. The following JSONC example documents the keys; the actual file must contain valid JSON without comments. Keep the existing generated secret and HWID rather than replacing the entire file with this example. After a manual edit, save the file and restart Decky Loader.

```jsonc
{
  "subscriptions": {
    // Key: subscription name; corresponding file: subscriptions/<name>.yaml
    // Remote/local-file URL, or local:// marker for an imported file
    "Example": "https://vpn.example/subscription.yaml",
    "Imported": "local://Imported"
  },
  "current": "Example",               // Current subscription; absent until selected
  "dashboard": "yacd",                // Current dashboard; absent until selected
  "secret": "RANDOM_SECRET",           // Controller secret; generated when absent
  "override_dns": true,               // Override DNS; default: true
  "enhanced_mode": "fake-ip",          // fake-ip or redir-host; default: fake-ip
  "controller_port": 9090,            // Mihomo controller port; default: 9090
  "external_port": 50581,             // External importer port; default: 50581
  "allow_remote_access": false,       // Remote access to controller; default: false
  "autostart": false,                 // Start core when plugin loads; default: false
  "timeout": 15.0,                    // Request timeout in seconds; default: 15.0
  "user_agent_override": "",           // Override subscription User-Agent; default: empty
  "subscription_hwid": "a618df94-a771-48c7-a2ae-d21104081e8a", // Example UUIDv4; generated
  "debounce_time": 10.0,              // Version query cache time in seconds; default: 10.0
  "disable_verify": false,            // Disable SSL verification; default: false
  "external_run_bg": false,           // Keep external importer running; default: false
  "auto_check_update": true,          // Check updates when plugin loads; default: true
  "auto_update_subscription": false,  // Update subscriptions when frontend loads; default: false
  "skip_steam_download": false,       // Add Steam download bypass rules; default: false
  "log_level": "INFO",                // Plugin log level; default: INFO
  "webdav_url": "",                    // Settings backup URL; default: empty
  "webdav_username": "",               // WebDAV username; default: empty
  "webdav_password": ""                // WebDAV password; default: empty
}
```

The `subscriptions` dictionary defaults to `{}`. `current` and `dashboard` are optional; the values above are examples. HTTP(S) and `file://` URLs can be downloaded. Uploading a subscription file stores a `local://<name>` marker; these imported files are excluded from remote updates.

### Subscription request headers

Downloads, individual updates, and bulk updates of remote subscriptions share the same header construction. The external importer calls the same backend methods.

| Header | Value |
| --- | --- |
| `User-Agent` | The built-in Mihomo/Clash string or a nonempty `user_agent_override`. |
| `X-Hwid` | The saved UUIDv4 from `subscription_hwid`. |
| `x-device-os` | `Linux`, the OS family that includes SteamOS. |
| `x-ver-os` | `VERSION_ID` from `os-release`; fallback: `unknown`. |
| `x-device-model` | The Steam Deck model detected through DMI; fallback: `Steam Deck`. |

The `device_info` module uses only the Python standard library. It reads the OS version through `platform.freedesktop_os_release()` from `/etc/os-release` or `/usr/lib/os-release`. If the file is unavailable, `VERSION_ID` is empty, or the value is unsuitable for safe use in an HTTP header, the plugin sends `unknown`.

Model detection checks the DMI `product_name` field and, when needed, `board_name`: Jupiter maps to `Steam Deck LCD`, and Galileo maps to `Steam Deck OLED`. If no recognized model is found, the plugin sends `Steam Deck`.

The standard library caches the parsed `os-release` data until the process restarts. After an OS update, restart the plugin or Decky Loader to refresh the reported version; rebooting the device also refreshes this information. No additional settings keys are required for these headers. `user_agent_override` replaces only `User-Agent`, retaining the HWID and all three device headers. The existing `subscription_hwid` is retained across OS updates.

### HWID lifecycle and errors

`subscription_hwid` is a random identifier of the installation, not a value derived from the device hardware. It is generated and saved before subscription requests and reused as `X-Hwid` for imports, individual updates, and updates of all remote subscriptions. The external importer calls the same backend.

The stored value must be a canonical UUIDv4 with hyphens; missing or invalid values are replaced with a new UUIDv4 when settings load. A valid value survives plugin restarts and upgrades while settings are retained. Deleting settings generates a new identity. A WebDAV backup includes the identifier: restoring it preserves the backup's identity, including when the backup is copied to another device. Restoring an older backup without this key generates a new identity.

Subscription headers are checked before a profile is saved or validated, both for HTTP 200 and HTTP errors. Header names are case-insensitive; values are stripped and compared to `true` without regard to case.

| Server signal | Backend result | User-facing behavior |
| --- | --- | --- |
| `x-hwid-max-devices-reached: true` | `HWID_MAX_DEVICES_REACHED` | Localized device-limit message in the plugin and external importer. |
| `x-hwid-not-supported: true` | `SUBSCRIPTION_REQUEST_FAILED` | Generic localized subscription error; the reason is logged. |
| `x-hwid-limit: true` | `SUBSCRIPTION_REQUEST_FAILED` | Generic localized subscription error; the reason is logged. |

The specific device-limit flag takes precedence if several flags are set. These refusals leave an existing profile intact, even when the response contains valid fallback YAML. An update also validates the new profile before atomically replacing the old file; temporary files are removed on failure.

## Build and release

The workflow is [`.github/workflows/build.yaml`](../.github/workflows/build.yaml). It runs regression tests, builds the frontend with Node.js 24 and pnpm, and packages the plugin. To run the same main checks locally:

```sh
python3 -m unittest discover -s tests -v
pnpm install --no-frozen-lockfile
pnpm build
```

Enable GitHub Actions in the fork before publishing. Pull requests and pushes to `main` build artifacts. Pushes to `dev` also publish the `nightly` prerelease. A `v` tag, such as `v1.3.7-HWID`, builds and publishes a stable GitHub Release unless its name contains `pre`.

Every release contains exactly these four assets:

| Asset | Contents |
| --- | --- |
| `DeckyClash.zip` | Small plugin package; Mihomo, dashboards, and Geo files are downloaded through the installation guide. |
| `DeckyClash-full-linux-amd64.zip` | Plugin, amd64 Mihomo, dashboards, and Geo files for Steam Deck and other x86-64 devices. |
| `DeckyClash-full-linux-arm64.zip` | Corresponding full package for ARM64 devices. |
| `version.txt` | Version used by update checks and the online installer. |

All three ZIPs have one top-level `DeckyClash/` directory and can be installed through Decky Settings → Developer. **Install Plugin from ZIP File → Browse** requires the ZIP to be on the target device. **Install Plugin from URL** downloads the selected asset over the internet. See the [installation instructions](../README_EN.md#install). The separate `install.sh` online installer remains an additional method; releases do not include self-extracting `.sh` installers.

The workflow downloads resource versions available at build time when assembling full packages. `amd64` and `arm64` packages differ in the Mihomo executable. Their bundled resources are imported on first load as described above.

### Version names and manual launch

For the tag `v1.3.7-HWID`, `version.txt` contains `v1.3.7-HWID` and the packaged `package.json` contains `1.3.7-HWID`. Non-`v`-tag builds use `nightly-YYMMDD-SHORTSHA` in both files, with a UTC date and the first seven commit characters. A build on `main` has this generated version but only uploads artifacts; it does not publish a nightly release.

If the automatic tag build did not start, manually dispatch the workflow at the same tag:

```sh
gh workflow run build.yaml --repo vrbeeshop/DeckyClash-HWID --ref v1.3.7-HWID
```

`workflow_dispatch` has no inputs. Its behavior follows the selected ref: a `v` tag publishes a release, `main` only builds artifacts, and `dev` publishes `nightly`. Dispatching `main` is therefore not a substitute for dispatching the release tag.
