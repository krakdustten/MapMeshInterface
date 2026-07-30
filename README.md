# MapMe Home Assistant Integration

HACS custom integration for [mapme.sh](https://mapme.sh) that exposes mapper stats as Home Assistant sensors and includes a Lovelace profile card.

## Features

- Polls `https://mapme.sh/api/user/<user_id>` on a configurable interval (default 15 minutes)
- One device and sensor set per configured user
- Profile sensor with full badge/metadata attributes for the Lovelace card
- Dedicated sensors for rank, points, samples, hexes, active days, and repeaters
- Multi-user support via UI or YAML
- Theme-native Lovelace card auto-registered on setup

## Installation

1. Add this repository as a [HACS custom repository](https://hacs.xyz/docs/faq/custom_repositories/).
2. Install **MapMe** from HACS → Integrations.
3. Restart Home Assistant.

## Configuration

### Config flow (UI)

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **MapMe**.
3. Enter your MapMe user ID (public key from mapme.sh).
4. Repeat to add additional users.

### YAML (multi-user)

```yaml
mapmesh:
  scan_interval: 900  # optional default seconds
  users:
    - user_id: "2577e905519e6071f776f32bc3d371a7b27b7c18cbd80462a7e64ef07319ac47"
      name: "Dylan"          # optional display override
      scan_interval: 600     # optional per-user seconds
    - user_id: "<other_pubkey>"
```

Each `users` entry creates one config entry. Duplicate `user_id` values are rejected.

### Options

Per-user scan interval can be changed under **Configure** on the integration entry (60–86400 seconds).

## Entities

Per configured user:

| Entity | State | Notes |
|--------|-------|-------|
| Profile | Points | Full attributes + badges for the card |
| Rank | Leaderboard rank | |
| Points | Total points | |
| Total samples | Sample count | |
| Unique hexes | Hexes visited | |
| Pioneer hexes | First-mapper hexes | |
| Active days | Days active | |
| Unique repeaters | Repeaters heard | |

## Lovelace card

Add a card per user pointing at that user's profile sensor:

```yaml
type: custom:mapmesh-card
entity: sensor.dylan_g_profile
```

The card shows name, hardware, rank, points, a stats grid, and badges with tier colors and progress.

## Development

```bash
pip install -r requirements_test.txt
pytest
```

## License

MIT
