<div align="center">
   <img src="./assets/logo.svg" width="400" height="200" alt="Decky Clash">
   <div>
      <img src="https://img.shields.io/github/check-runs/vrbeeshop/DeckyClash-HWID/main" alt="Сборка">
      <img src="https://img.shields.io/github/v/release/vrbeeshop/DeckyClash-HWID" alt="Версия">
      <img src="https://img.shields.io/github/downloads/vrbeeshop/DeckyClash-HWID/total" alt="Загрузки">
      <img src="https://img.shields.io/badge/license-BSD 3--Clause-blue" alt="Лицензия">
   </div>
   <p>
      <i>Лёгкий клиент Clash/Mihomo для SteamOS с поддержкой HWID</i>
   </p>
   <p>
      <b>RU</b> | <b><a href="./README_EN.md">English</a></b> | <b><a href="./README_CN.md">中文</a></b>
   </p>
</div>

> [!CAUTION]
> Если вы являетесь гражданином Китайской Народной Республики или постоянно проживаете на её территории, перед использованием внимательно прочитайте и убедитесь, что понимаете [условия использования и отказ от ответственности](./README_CN.md#免责声明). Скачивание, установка или использование проекта означает согласие с этими условиями и принятие соответствующей ответственности.

Форк [chenx-dust/DeckyClash](https://github.com/chenx-dust/DeckyClash) с поддержкой HWID в подписках.

## Возможности

- ✅ **Функциональность Mihomo:** используется ядро [Mihomo](https://github.com/MetaCubeX/mihomo).
- 🚀 **Быстрая работа:** оптимизированные интерфейс и серверная часть.
- 📦 **Удобная настройка:** импорт подписок, внешний импортёр и мастер установки ресурсов.
- 🔒 **Настройки безопасности:** случайный пароль контроллера и управление удалённым доступом.
- 🆔 **Подписки с HWID:** постоянный идентификатор устройства и понятное сообщение о достижении лимита устройств.
- ⚙️ **Поддерживаемый код:** Python и Node.js.
- 💡 **Обновления:** встроенные средства обновления плагина и сторонних ресурсов.
- 🌍 **Языки интерфейса:** русский, английский и упрощённый китайский.

## Скриншоты

![Интерфейс плагина](./assets/screenshots.png)

## Лицензия

Проект распространяется по лицензии **BSD 3-Clause License**. Подробности — в [LICENSE](./LICENSE).

## Установка

### Подготовка

Установите [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader):

```sh
curl -L https://github.com/SteamDeckHomebrew/decky-installer/releases/latest/download/install_release.sh | sh
```

### Установка через Decky — основной способ

Выберите ZIP в [последнем выпуске](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest):

| Файл выпуска | Когда выбирать |
| --- | --- |
| [DeckyClash.zip](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/DeckyClash.zip) | Небольшой пакет плагина, около 4 МБ. После установки мастер скачает Mihomo, панели управления и Geo-файлы. |
| [DeckyClash-full-linux-amd64.zip](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/DeckyClash-full-linux-amd64.zip) | Полный пакет с Mihomo и ресурсами для **Steam Deck LCD/OLED** и других устройств x86-64. |
| [DeckyClash-full-linux-arm64.zip](https://github.com/vrbeeshop/DeckyClash-HWID/releases/latest/download/DeckyClash-full-linux-arm64.zip) | Полный пакет **только для устройств ARM64**. |

1. В игровом режиме откройте меню быстрого доступа (**…**) → **Decky** → **Настройки** (значок шестерёнки).
2. В разделе **General** включите **Developer mode**, затем откройте вкладку **Developer**.
3. Установите выбранный ZIP одним из способов:
   - **Install Plugin from ZIP File** → **Browse**: сначала скачайте или перенесите ZIP на Deck, например в `~/Downloads`, затем выберите этот файл в Decky.
   - **Install Plugin from URL**: вставьте прямую ссылку на выбранный ZIP и нажмите **Install**. Decky скачает архив через интернет; это относится и к полному пакету.
4. Откройте **Decky Clash**. Если установлен небольшой `DeckyClash.zip`, выберите в мастере установки **Установить всё**, чтобы скачать необходимые ресурсы. В полных ZIP ресурсы уже включены; плагин перенесёт их при первой загрузке.

Для Steam Deck нужен полный пакет **amd64**. Небольшой пакет автоматически выбирает архитектуру Mihomo при скачивании ресурсов. Размер архивов и версии включённых ресурсов могут меняться от выпуска к выпуску.

### Онлайн-скрипт — дополнительный способ

Небольшой скрипт `install.sh`, около 10 КБ, скачивает плагин и ресурсы во время установки:

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash
```

Скрипт загружает последний выпуск плагина, Mihomo, рекомендуемые панели управления и необходимые Geo-файлы. Для установки требуется доступ к GitHub.

Справка по параметрам, включая установку ночной сборки и обновление ресурсов:

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash -s -- --help
```

## Обновление

Плагин автоматически проверяет обновления при входе в интерфейс Steam. Если доступна новая версия, появится уведомление.

### Через плагин

1. Откройте меню быстрого доступа и выберите **Decky Clash**.
2. В разделе **Версия** нажмите **Управление обновлениями**.
3. Дождитесь проверки: доступная версия появится в строке **Последняя версия**.
4. Если она отличается от установленной, нажмите кнопку обновления.

### Полное обновление

Повторите шаги из раздела [«Установка»](#установка) с новым ZIP.

### Обновление сторонних ресурсов

Используйте встроенные средства обновления или выполните:

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash -s -- --without-plugin --without-restart --yes
```

## Удаление

> [!CAUTION]
> Скрипт удалит все файлы Decky Clash, включая настройки, подписки и скачанные панели управления. Используйте этот способ с осторожностью.

```sh
curl -L https://raw.githubusercontent.com/vrbeeshop/DeckyClash-HWID/main/install.sh | bash -s -- --clean-uninstall
```

## Частые вопросы

См. [FAQ.md](./docs/FAQ.md#frequently-asked-questions).

## Разработка

См. [руководство для разработчиков](./docs/DEV_GUIDE.md).

## Благодарности

- [chenx-dust/DeckyClash](https://github.com/chenx-dust/DeckyClash): исходный проект Decky Clash.
- [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo): ядро, на котором работает Decky Clash.
- [ruamel-yaml](https://sourceforge.net/projects/ruamel-yaml/): библиотека обработки YAML.
- [YukiCoco/ToMoon](https://github.com/YukiCoco/ToMoon): проект, вдохновивший авторов Decky Clash.
- [ba.sh](https://app.ba.sh/): сервис коротких ссылок для проектов с открытым исходным кодом.
