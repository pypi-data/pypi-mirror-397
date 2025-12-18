# opentele-py313

<p align="center">
<img src="https://raw.githubusercontent.com/thedemons/opentele/main/opentele.png" alt="logo" width="180"/>
</p>

## Python 3.13+ Compatible Fork

This is a **Python 3.13+ compatible fork** of the [original opentele library](https://github.com/thedemons/opentele) by [thedemons](https://github.com/thedemons).

### What's Changed?

- **Python 3.13 Compatibility**: Fixed compatibility issues with Python 3.13 by handling new class attributes (`__firstlineno__` and `__static_attributes__`) in the `extend_class` decorator.
- All original functionality remains intact.

### Original Project

This fork is based on [opentele v1.15.1](https://github.com/thedemons/opentele). All credit for the original library goes to [thedemons](https://github.com/thedemons).

**Original repository**: https://github.com/thedemons/opentele

---

## Features
- Convert [Telegram Desktop](https://github.com/telegramdesktop/tdesktop) **tdata** sessions to [telethon](https://github.com/LonamiWebs/Telethon) sessions and vice versa.
- Use **telethon** with [official APIs](#authorization) to avoid bot detection.
- Randomize [device info](https://opentele.readthedocs.io/en/latest/documentation/authorization/api/#generate) using real data that recognized by Telegram server.

## Dependencies

- [telethon](https://github.com/LonamiWebs/Telethon) - Widely used Telegram's API library for Python.
- [tgcrypto](https://github.com/pyrogram/tgcrypto) - AES-256-IGE encryption to works with `tdata`.
- [pyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Used by Telegram Desktop to streams data from files.

## Installation

### For Python 3.13+
Install this fork from PyPI:
```bash
pip install --upgrade opentele-py313
```

### For Python 3.12 and below
Use the original library:
```bash
pip install --upgrade opentele
```

## First Run
Load TDesktop from tdata folder and convert it to telethon, with a custom API:
```python
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, CreateNewSession, UseCurrentSession
import asyncio

async def main():
    
    # Load TDesktop client from tdata folder
    tdataFolder = r"C:\Users\<username>\AppData\Roaming\Telegram Desktop\tdata"
    tdesk = TDesktop(tdataFolder)

    # Using official iOS API with randomly generated device info
    # print(api) to see more
    api = API.TelegramIOS.Generate()

    # Convert TDesktop session to telethon client
    # CreateNewSession flag will use the current existing session to
    # authorize the new client by `Login via QR code`.
    client = await tdesk.ToTelethon("newSession.session", CreateNewSession, api)

    # Although Telegram Desktop doesn't let you authorize other
    # sessions via QR Code (or it doesn't have that feature),
    # it is still available across all platforms (APIs).

    # Connect and print all logged in devices
    await client.connect()
    await client.PrintSessions()

asyncio.run(main())
```

## Authorization
**opentele** offers the ability to use **official APIs**, which are used by official apps. You can check that out [here](https://opentele.readthedocs.io/en/latest/documentation/authorization/api/#class-api).
<br>

According to [Telegram TOS](https://core.telegram.org/api/obtaining_api_id#using-the-api-id): *all accounts that sign up or log in using unofficial Telegram API clients are automatically put under observation to avoid violations of the Terms of Service*.
<br>
<br>
It also uses the **[lang_pack](https://core.telegram.org/method/initConnection)** parameter, of which [telethon can't use](https://github.com/LonamiWebs/Telethon/blob/dd51aea4db90fd255a14e27192e221c70b45e105/telethon/_client/telegrambaseclient.py#L197) because it's for official apps only.
<br>
Therefore, **there are no differences** between using opentele and official apps, the server can't tell you apart.

## Incoming Features
- [x] Writing data to tdata for converting telethon sessions to tdesktop.
- [x] Random device information for [initConnection](https://core.telegram.org/method/initConnection) to avoid spam-detection.
- [ ] Add support for [pyrogram](https://github.com/pyrogram/pyrogram).
- [ ] Develop opentele-tui using [textual](https://github.com/Textualize/textual) for non-experience user.

## Examples
The best way to learn anything is by looking at the examples. Am I right?

- Example on [readthedocs](https://opentele.readthedocs.io/en/latest/examples/)
- Example on [github](./examples)

## Documentation [![documentation](https://readthedocs.org/projects/opentele/badge/?version=latest&style=flat)](https://opentele.readthedocs.io/)
- Read documentation on [readthedocs](https://opentele.readthedocs.io/en/latest/documentation/telegram-desktop/tdesktop/)
- Read documentation on [github](https://github.com/thedemons/opentele/tree/main/docs-github)
