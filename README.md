# Waze Police Alert Monitor

A Python-based monitoring tool that continuously checks Waze for police alerts in a specified geographic area and sends notifications via Pushover and Discord webhooks.

## Features

- **Real-time Monitoring**: Continuously monitors Waze for police alerts in configurable geographic bounds
- **Multiple Notification Channels**: Sends instant notifications via Pushover and Discord webhooks
- **Geocoding**: Converts coordinates to street names using OpenStreetMap Nominatim
- **Flexible Bounds**: Configurable monitoring area via environment variables or command-line arguments
- **Interactive Map**: Visualize monitoring bounds on an interactive map
- **Dry Run Mode**: Test functionality without sending notifications
- **Comprehensive Logging**: Detailed logging to both file and console

## Prerequisites

- Python 3.7+
- Pushover account and API credentials (optional)
- Discord server with webhook access (optional)
- Internet connection for Waze API and geocoding services

## Installation

1. Clone or download the script
2. Install required dependencies:

### Using pip
```bash
pip install aiohttp asyncio typer folium webbrowser discord
```

### Using pipenv (Recommended)
```bash
# Install pipenv if you haven't already
pip install pipenv

# Create a virtual environment and install dependencies
pipenv install

# Activate the virtual environment
pipenv shell
```

## Configuration

### Environment Variables

Set the following environment variables:

```bash
# Geographic bounds (default: LA County)
export BOUNDS_TOP="34.8233"      # Top latitude (northern boundary)
export BOUNDS_BOTTOM="32.5123"   # Bottom latitude (southern boundary)
export BOUNDS_LEFT="-119.2073"   # Left longitude (western boundary)
export BOUNDS_RIGHT="-117.6461"  # Right longitude (eastern boundary)

# Pushover configuration (optional)
export PUSHOVER_API_KEY="your_pushover_api_key"
export PUSHOVER_USER_KEYS="user_key1,user_key2,user_key3"  # Comma-separated list

# Discord webhook configuration (optional)
export DISCORD_WEBHOOK_URLS="https://discord.com/api/webhooks/URL1,https://discord.com/api/webhooks/URL2"  # Comma-separated list
```

### Pushover Setup (Optional)

1. Create a Pushover account at [pushover.net](https://pushover.net)
2. Create a new application to get your API key
3. Note your user key from your account settings
4. Add both keys to your environment variables

### Discord Webhook Setup (Optional)

1. Open Discord and go to your server
2. Right-click on the channel where you want notifications
3. Select "Edit Channel" → "Integrations" → "Webhooks"
4. Click "Create Webhook"
5. Give it a name (e.g., "Waze Pinger")
6. Copy the webhook URL and add it to your environment variables
7. For multiple channels, create multiple webhooks and separate URLs with commas

**Note**: You can use both Pushover and Discord simultaneously, or just one of them. At least one notification method must be configured for the application to work.

## Usage

### Continuous Monitoring

Start continuous monitoring with default settings:

```bash
# Using pip
python main.py monitor

# Using pipenv
pipenv run python main.py monitor
```

Monitor with custom interval (e.g., every 2 minutes):

```bash
# Using pip
python main.py monitor --interval 120

# Using pipenv
pipenv run python main.py monitor --interval 120
```

Monitor with custom geographic bounds:

```bash
# Using pip
python main.py monitor --top 34.5 --bottom 34.0 --left -118.5 --right -118.0

# Using pipenv
pipenv run python main.py monitor --top 34.5 --bottom 34.0 --left -118.5 --right -118.0
```

### Single Check

Check for alerts once and exit:

```bash
# Using pip
python main.py check-once

# Using pipenv
pipenv run python main.py check-once
```

With custom bounds:

```bash
# Using pip
python main.py check-once --top 34.5 --bottom 34.0 --left -118.5 --right -118.0

# Using pipenv
pipenv run python main.py check-once --top 34.5 --bottom 34.0 --left -118.5 --right -118.0
```

### Dry Run Mode

Test without sending notifications:

```bash
# Using pip
python main.py monitor --dry-run

# Using pipenv
pipenv run python main.py monitor --dry-run
```

### Visualize Monitoring Area

Show current bounds and create an interactive map:

```bash
# Using pip
python main.py show-bounds

# Using pipenv
pipenv run python main.py show-bounds
```

Open map automatically in browser:

```bash
# Using pip
python main.py show-bounds --open

# Using pipenv
pipenv run python main.py show-bounds --open
```

Save map to custom location:

```bash
# Using pip
python main.py show-bounds --save /path/to/map.html

# Using pipenv
pipenv run python main.py show-bounds --save /path/to/map.html
```

## Command Line Options

### Monitor Command
- `--top, -t`: Top latitude bound
- `--bottom, -b`: Bottom latitude bound
- `--left, -l`: Left longitude bound
- `--right, -r`: Right longitude bound
- `--interval, -i`: Monitoring interval in seconds (default: 300)
- `--dry-run`: Run without sending notifications

### Check-once Command
- `--top, -t`: Top latitude bound
- `--bottom, -b`: Bottom latitude bound
- `--left, -l`: Left longitude bound
- `--right, -r`: Right longitude bound
- `--dry-run`: Run without sending notifications

### Show-bounds Command
- `--open, -o`: Open map in browser automatically
- `--save, -s`: Save map to specific path

## Output

### Logs
- All activity is logged to `waze_monitor.log`
- Console output shows real-time status
- Log format: `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`

### Notifications
When police alerts are detected, you'll receive notifications via your configured channels:

**Pushover Notifications:**
- Title: "Police Alert Nearby"
- Message: Street name and city information

**Discord Notifications:**
- Rich embed with red color scheme
- Title: "🚨 Police Alert Nearby"
- Description: Street name and city information
- Username: "Waze Pinger" with custom avatar
- Footer: "Waze Pinger Alert System"

### Map Output
The `show-bounds` command generates an HTML file with:
- Interactive map centered on monitoring area
- Red rectangle showing monitoring bounds
- Corner markers for reference
- Center point marker

## Technical Details

### API Endpoints
- **Waze API**: `https://www.waze.com/live-map/api/georss`
- **Geocoding**: OpenStreetMap Nominatim API
- **Notifications**: Pushover API and Discord Webhook API

### Data Flow
1. Script queries Waze API for alerts in specified bounds
2. Filters for police alerts only
3. Converts coordinates to street names via geocoding
4. Sends notifications to all configured channels (Pushover and/or Discord)
5. Waits for specified interval before next check

### Error Handling
- Network errors are logged and retried
- Invalid responses are logged with details
- Geocoding failures fall back to "Unknown Street"
- Main loop continues running despite individual errors

## Troubleshooting

### Common Issues

**No notifications received:**
- Verify at least one notification method is configured (Pushover or Discord)
- Check Pushover API key and user keys are correct (if using Pushover)
- Verify Discord webhook URLs are valid (if using Discord)
- Check internet connectivity
- Test with `--dry-run` to verify monitoring works

**No alerts found:**
- Verify geographic bounds are correct
- Check if monitoring area has active police alerts
- Try expanding the monitoring area

**Geocoding errors:**
- Nominatim has rate limits, errors are normal
- Script falls back to "Unknown Street" when geocoding fails

**Discord webhook errors:**
- Verify webhook URL is complete and valid
- Check that the Discord server/channel still exists
- Ensure the webhook hasn't been deleted or disabled
- Test webhook manually in Discord first

**Network errors:**
- Check internet connection
- Waze API may be temporarily unavailable
- Script will retry automatically

### Testing Discord Webhooks

To test your Discord webhook configuration:

```bash
# Test with a simple message
python -c "
import os
import asyncio
import aiohttp
import discord
from discord import Webhook

async def test_webhook():
    webhook_url = 'YOUR_WEBHOOK_URL_HERE'
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        embed = discord.Embed(title='🧪 Test', description='Discord webhook test', color=0xFF0000)
        await webhook.send(embed=embed, username='Waze Pinger')
        print('✅ Discord webhook test successful!')

asyncio.run(test_webhook())
"
```

### Debug Mode

Enable verbose logging by modifying the logging level in the script:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Legal and Ethical Considerations

- This tool is for educational and personal use only
- Respect Waze's terms of service and API usage policies
- Use responsibly and in accordance with local laws
- Do not use for illegal activities or harassment
- Be mindful of privacy and data protection regulations

## Architecture

The application is built with a modular architecture:

- **`main.py`**: Main application logic and CLI interface
- **`alert_cache.py`**: Persistent cache management for duplicate alert prevention
- **`notification_provider.py`**: Unified notification system supporting Pushover and Discord
- **`Pipfile`**: Dependency management with pipenv

### Key Features

- **Modular Design**: Separate classes for caching and notifications
- **Multiple Notification Channels**: Support for both Pushover and Discord webhooks
- **Flexible Configuration**: Environment variable-based configuration
- **Error Handling**: Comprehensive error handling and logging
- **Extensible**: Easy to add new notification providers

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool.

## License

This project is provided as-is for educational purposes. Use at your own risk and in accordance with applicable laws and terms of service. 