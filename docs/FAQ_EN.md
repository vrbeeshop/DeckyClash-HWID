# Frequently Asked Questions

[RU](./FAQ.md) | **English**

[Installation](../README_EN.md#install) · [Development Guide](./DEV_GUIDE_EN.md)

## Installation

### How do I install DeckyClash-HWID specifically?

This fork is distributed through [vrbeeshop/DeckyClash-HWID releases](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest). Install a ZIP through **Decky → Settings → Developer**. If that tab is hidden, enable **Developer mode** under **General**. See the [README](../README_EN.md#install) for the full instructions.

Choose a package:

- `DeckyClash.zip` — the small plugin package, about 4 MB. On first launch, choose **Install All** in the installation guide to download Mihomo, dashboards, and Geo files.
- `DeckyClash-full-linux-amd64.zip` — the full package with the core and resources for Steam Deck LCD/OLED and other x86-64 devices.
- `DeckyClash-full-linux-arm64.zip` — the full package for ARM64 devices.

For **Install Plugin from ZIP File → Browse**, download or copy the ZIP onto the Deck first, then select that file. For **Install Plugin from URL**, enter the direct ZIP download URL: Decky downloads it over the internet. This also applies to full packages. The small online `install.sh` script described in the README provides another installation method.

### Can I use Decky Clash from the Decky Store?

Use this fork's own releases and instructions for its features. The Decky Clash name alone does not establish that you have DeckyClash-HWID installed. This fork's built-in updater downloads the plugin from `vrbeeshop/DeckyClash-HWID`.

### Why is the version unavailable or a resource download failing?

The current code reads the version number from a `version.txt` file attached to a GitHub release. Plugin version checks use [this file](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/version.txt); Mihomo obtains its version from `MetaCubeX/mihomo` releases. The plugin does not call the GitHub API for this check.

Check access to GitHub release assets and the error message in the plugin log. Version retrieval can fail because of network access, a timeout, or a missing file in the selected release. If downloads are unavailable on the Deck, download the full ZIP for its architecture on another device, copy it onto the Deck, and install it with **Install Plugin from ZIP File**.

## Settings and logs

### Where are the advanced settings?

The default settings file is `~/homebrew/settings/DeckyClash/config.json`. You can configure `user_agent_override`, `log_level`, timeouts, and other options there. See the [Development Guide](./DEV_GUIDE_EN.md) for the settings list.

After editing the file manually, save valid JSON and restart Decky Loader so that the plugin reloads its settings:

```sh
sudo systemctl restart plugin_loader.service
```

Restarting stops the running Mihomo instance managed by the plugin.

### Where are the logs, and how do I enable detailed logging?

Plugin logs are stored in `~/homebrew/logs/DeckyClash`. Mihomo output is written to `core.log`; this file is opened afresh when the core starts.

For detailed logging, set `"log_level": "DEBUG"` in `config.json` and restart Decky Loader. The default is `INFO`; `WARNING` and `ERROR` are also supported. Remove subscription links, passwords, and other secrets from a copy of the log before sharing it.

## Subscriptions and HWID

### How do I add a subscription or import a file?

Open **Decky Clash → Import**, enter a Clash/Mihomo subscription link, and start the download. The external importer on the same page lets you open a web panel through a QR code or URL and import a subscription link or upload a configuration file. You can rename a subscription afterwards on the management page.

Profiles are saved as `~/homebrew/settings/DeckyClash/subscriptions/<name>.yaml`. A file uploaded through the external importer is stored as a local subscription and is not updated over the network. Add an HTTP(S) subscription link for a profile that needs remote updates.

### Where does HWID come from? Do I need to enter it myself?

If no identifier has been saved yet, the plugin generates a random UUIDv4 and saves it as `subscription_hwid` in `config.json`. This identifier is sent in the `X-Hwid` header when downloading or updating remote subscriptions. You do not need to enter it manually for normal use.

The HWID persists across restarts and is included in settings backups. Deleting settings generates a new identifier; restoring a backup restores its identifier. A missing or invalid `subscription_hwid` value is also replaced with a new UUIDv4 when settings are loaded. Your provider may treat a changed identifier as a new device.

### What does “The device limit for this subscription has been reached” mean?

The subscription server returned `x-hwid-max-devices-reached: true`. Remove an unused device in your provider account, if that option is available, or contact your provider.

The plugin checks this header in both HTTP 200 responses and HTTP errors. A refused update preserves the saved configuration. The message appears during import, manual updates, and automatic subscription updates.

### Why does the plugin show “Could not retrieve the subscription. See the plugin log for details”?

This is the message for other HWID restrictions reported through `x-hwid-not-supported` or `x-hwid-limit`, when the more specific device-limit signal is absent. The detailed reason is written to the plugin log. A refused update does not replace the saved configuration with the server's response.

### Why does another client receive a different profile from the same URL?

A provider may select the subscription format based on `User-Agent`. By default, the plugin sends a built-in User-Agent for Mihomo/Clash clients. If your provider requires a different value, set `user_agent_override` in `config.json` and restart Decky Loader. An empty value restores the built-in User-Agent.

### How do I override profile settings?

TUN and DNS templates and general overrides are stored in `~/homebrew/plugins/DeckyClash/override.yaml`. The DNS override toggle is available in the plugin interface. See the [template file](../defaults/override.yaml) for its structure and examples.

Keep a separate copy of your changes: plugin updates replace the files in the plugin directory, including `override.yaml`.

## Updates

### How do I update the plugin, Mihomo, and resources?

Open **Manage Upgrades** in the plugin. DeckyClash and Mihomo have separate rows for installed and available versions, channel selection, and update buttons. Mihomo can be updated separately from the plugin; its archive is selected for the device's architecture. Geo files and dashboards have separate reinstall buttons on the same page.

When automatic checking is enabled, the plugin checks for new versions on load and shows a notification if an update is available. To check manually, click the available version on the update page. You can also update the plugin by installing a new ZIP using the [README instructions](../README_EN.md#install).

### Why is the latest version shown as a cross mark?

A cross mark means that the interface did not receive an available version. Check the `version.txt` download for the selected channel and the plugin log. The plugin offers latest-release and nightly channels; Mihomo offers the stable Meta channel and Alpha. A missing release file or a network error does not mean that the installed version is damaged.
