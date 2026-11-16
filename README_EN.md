<div align="center">
   <img src="./assets/logo.svg" width="400" height="200" alt="Decky Clash">
   <div>
      <img src="https://img.shields.io/github/check-runs/vrbeeshop/DeckyClash-HWID/main" alt="Actions">
      <img src="https://img.shields.io/github/v/release/vrbeeshop/DeckyClash-HWID" alt="Release">
      <img src="https://img.shields.io/github/downloads/vrbeeshop/DeckyClash-HWID/total" alt="Downloads">
      <img src="https://img.shields.io/badge/license-BSD 3--Clause-blue" alt="License">
   </div>
   <p>
      <i>Light-weight Clash/Mihomo proxy client for Steam OS</i>
   </p>
   <p>
      <b><a href="./README.md">RU</a></b> | <b>EN</b>
   </p>
</div>

Fork of [chenx-dust/DeckyClash](https://github.com/chenx-dust/DeckyClash) with HWID subscription support.

## Features

- ✅ **Full featured:** powered by the [Mihomo](https://github.com/MetaCubeX/mihomo) core
- 🚀 **Blazing fast:** optimized frontend and backend
- 📦 **Easy to use:** out of the box, with subscriptions importer and installation guide, etc.
- 🔒 **Focus on security:** random controller password, controllable outside access, etc.
- 🆔 **HWID subscriptions:** persistent device identity and readable device-limit errors
- ⚙️ **Friendly to maintain:** written by Python and Node.js
- 💡 **Keep update:** built-in upgrade tool to keep 3rd-party resources update
- 🌍 **Russian and English:** interface and documentation in both languages

## Screenshots

![Screenshots](./assets/screenshots.png)

## License

This project is licensed by **BSD 3-Clause License**. See more details in [LICENSE](./LICENSE).

## Install

### Prerequisite

Install [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader)

```sh
curl -L https://github.com/SteamDeckHomebrew/decky-installer/releases/latest/download/install_release.sh | sh
```

### Install through Decky (Recommended)

Choose a ZIP from [Latest Release](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest):

| Release asset | Choose this when |
| --- | --- |
| [DeckyClash.zip](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/DeckyClash.zip) | Small plugin package (about 4 MB). The installation guide downloads Mihomo, dashboards, and Geo files after installation. |
| [DeckyClash-full-linux-amd64.zip](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/DeckyClash-full-linux-amd64.zip) | Full package with Mihomo and resource files for **Steam Deck LCD/OLED** and other x86-64 devices. |
| [DeckyClash-full-linux-arm64.zip](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/DeckyClash-full-linux-arm64.zip) | Full package for **ARM64 devices only**. |

1. In Gaming Mode, open the Quick Access Menu (**…**) → **Decky** → **Settings** (gear icon).
2. In **General**, enable **Developer mode**, then open the **Developer** tab.
3. Install the chosen ZIP using either option:
   - **Install Plugin from ZIP File** → **Browse**: first download or copy the ZIP onto the Deck (for example, into `~/Downloads`), then select it in Decky.
   - **Install Plugin from URL**: paste the direct download URL of the chosen ZIP and select **Install**. This downloads the archive over the internet, including when you choose a full package.
4. Open **Decky Clash**. If you installed the small `DeckyClash.zip`, use the installation guide and select **Install All** to download the required resources. Full ZIPs already contain these resources; the plugin imports them on first load.

Steam Deck uses the **amd64** full package. The small package selects the appropriate Mihomo architecture when downloading resources. ZIP sizes and bundled resource versions vary by release.

### Online install script (Additional option)

The small `install.sh` script (about 10 KB) downloads the plugin and resources during installation:

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash
```

The installation script will download the latest release from Github, as well as necessary third-party resources such as the latest Mihomo core, recommended Dashboards, and the Geo files required by the core.

The script includes functions to download nightly versions and update third-party resources, which can be viewed through the `-h` parameter:

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash -s -- -h
```

## Upgrade

Plugin will automatically check for updates every time you enter the Steam interface. If there is a new version, a toast will be shown.

### Built-in upgrade

1. Enter the Quick Access Menu and select **Decky Clash**.
2. Find the **Version** column and click the **Manage Upgrades** button.
3. The program will automatically check for updates, and the **Latest Version** row will display.
4. If **Latest Version** and **Installed Version** are different, an upgrade button will be shown, click to start.

### Full upgrade

(Same as the [installation](#install) step)

### Upgrade Third-Party Resources

Use built-in upgrade or execute the following command:

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash -s -- --without-plugin --without-restart --yes
```

## Uninstall

> [!CAUTION]
> The script uninstalls Decky Clash, which will delete all files, including settings, subscriptions, downloaded Dashboards, etc. Please use with caution.

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash -s -- --clean-uninstall
```

## Frequently Asked Questions

See the [FAQ](./docs/FAQ_EN.md) for details.

## Development Guide

See the [Development Guide](./docs/DEV_GUIDE_EN.md) for details.

## Acknowledgements

- [chenx-dust/DeckyClash](https://github.com/chenx-dust/DeckyClash): the original Decky Clash project.
- [drode1/DeckyClash](https://github.com/drode1/DeckyClash): the initial HWID request implementation used as the basis for this fork.
- [Prizrak-Core](https://github.com/legiz-ru/Prizrak-Core): special thanks to the project and its contributors.
- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader): the platform that runs this plugin.
- [Mihomo](https://github.com/MetaCubeX/mihomo): the proxy core used by the plugin.
- [meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat): Geo data and rule sets downloaded by the plugin and included in full ZIPs.
- [yacd](https://github.com/haishanh/yacd), [metacubexd](https://github.com/MetaCubeX/metacubexd), and [zashboard](https://github.com/Zephyruso/zashboard): the available web dashboards.
- [ruamel.yaml](https://yaml.dev/doc/ruamel.yaml/): the library used to read and modify YAML configurations.
- [To Moon](https://github.com/YukiCoco/ToMoon): the inspiration for the original Decky Clash.
