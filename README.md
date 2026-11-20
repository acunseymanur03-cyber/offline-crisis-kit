# Offline Crisis Kit

A tiny, zero-dependency toolkit that turns any phone or computer into an **offline information and messaging hub** when the internet is down.

- **Local chat** for everyone connected to the same Wi-Fi network or phone hotspot, with a HELP flag for urgent messages
- **Offline reference pages**: first aid basics, safe drinking water, emergency communication plan, power and battery tips
- **No internet, no accounts, no installs**: Python 3.7+ standard library only

> **Status: early prototype (v0.1).** The server has been tested on Linux with automated HTTP checks. It has **not yet been tested on real Android/Termux devices, with multiple phones on a hotspot, or on solar power**. Community testing is very welcome. See [Roadmap](#roadmap).

> **Safety note:** The reference pages are a short, basic guide, not a substitute for training or professional help. They should be reviewed by qualified people before anyone relies on them. Always contact official emergency services when you can.

## Quick start

### Android (Termux)

1. Install [Termux](https://f-droid.org/packages/com.termux/) from F-Droid (the Play Store version is outdated).
2. While you still have internet, prepare once:
   ```
   pkg update
   pkg install python git
   git clone https://github.com/<your-username>/offline-crisis-kit
   ```
3. Later, with **no internet at all**:
   ```
   cd offline-crisis-kit
   python server.py
   ```
4. Turn on your phone's **Wi-Fi hotspot**. Other devices join it and open the address printed by the script (for example `http://192.168.x.x:8080`).

If the script cannot detect the address, check it in your phone's hotspot settings, or run `ip addr` / `ifconfig` in Termux.

### Linux / macOS / Windows

```
python server.py
```

Set a different port with `PORT=9000 python server.py`.

## How it works

| File | Purpose |
|------|---------|
| `server.py` | HTTP server, chat API, page renderer |
| `pages.py` | Built-in offline reference pages |
| `content/*.md` | *(optional)* extra pages; any `.md` file here is added automatically |
| `chat_log.jsonl` | Created at runtime; keeps chat history across restarts |

The chat uses simple polling (every 2 seconds). Messages are rendered as plain text, limited in length, and rate-limited per device.

## Important limitations

- **Not encrypted, not authenticated.** Anyone on the network can read and write. Use for emergencies and local coordination, never for private information.
- **Local network only.** This does not connect different cities or countries. Reaching further needs radio (HF/Winlink, LoRa/Meshtastic) or satellite links, which are on the roadmap as integration guides.
- **Power matters.** Offline software still needs batteries: keep a charged power bank, lower screen brightness, and consider a small solar panel.

## Roadmap

- [ ] Test on real Android devices over hotspot (and report results)
- [ ] Turkish, Spanish, German, French translations of the reference pages
- [ ] Expert review of all medical and safety content
- [ ] Offline Wikipedia via [Kiwix](https://kiwix.org) integration guide
- [ ] Raspberry Pi image: own Wi-Fi access point + solar-powered setup guide
- [ ] [Meshtastic](https://meshtastic.org) (LoRa) bridge for longer-range messages
- [ ] Optional message encryption with a shared passphrase

## Contributing

Corrections to the reference pages and device test reports are the most valuable contributions. Open an issue or pull request. To add a page, drop a Markdown file into `content/` (supports `#`, `##`, `- ` lists, `1.` lists and `**bold**`).

## License

MIT, see [LICENSE](LICENSE).
