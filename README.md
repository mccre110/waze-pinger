# Waze Police Alert Monitor

A Python-based monitoring tool that continuously checks Waze for police alerts in a specified geographic area and sends push notifications via Pushover.

## Features

- **Real-time Monitoring**: Continuously monitors Waze for police alerts in configurable geographic bounds
- **Push Notifications**: Sends instant notifications via Pushover when police alerts are detected
- **Geocoding**: Converts coordinates to street names using OpenStreetMap Nominatim
- **Flexible Bounds**: Configurable monitoring area via environment variables or command-line arguments
- **Interactive Map**: Visualize monitoring bounds on an interactive map
- **Dry Run Mode**: Test functionality without sending notifications
- **Comprehensive Logging**: Detailed logging to both file and console

## Prerequisites

- Python 3.7+
- Pushover account and API credentials
- Internet connection for Waze API and geocoding services

## Installation

1. Clone or download the script
2. Install required dependencies:

```bash
pip install aiohttp asyncio typer folium webbrowser
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

# Pushover configuration
export PUSHOVER_API_KEY="your_pushover_api_key"
export PUSHOVER_USER_KEYS="user_key1,user_key2,user_key3"  # Comma-separated list
```

### Pushover Setup

1. Create a Pushover account at [pushover.net](https://pushover.net)
2. Create a new application to get your API key
3. Note your user key from your account settings
4. Add both keys to your environment variables

## Usage

### Continuous Monitoring

Start continuous monitoring with default settings:

```bash
python main.py monitor
```

Monitor with custom interval (e.g., every 2 minutes):

```bash
python main.py monitor --interval 120
```

Monitor with custom geographic bounds:

```bash
python main.py monitor --top 34.5 --bottom 34.0 --left -118.5 --right -118.0
```

### Single Check

Check for alerts once and exit:

```bash
python main.py check-once
```

With custom bounds:

```bash
python main.py check-once --top 34.5 --bottom 34.0 --left -118.5 --right -118.0
```

### Dry Run Mode

Test without sending notifications:

```bash
python main.py monitor --dry-run
```

### Visualize Monitoring Area

Show current bounds and create an interactive map:

```bash
python main.py show-bounds
```

Open map automatically in browser:

```bash
python main.py show-bounds --open
```

Save map to custom location:

```bash
python main.py show-bounds --save /path/to/map.html
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
When police alerts are detected, you'll receive Pushover notifications with:
- Title: "Police Alert Nearby"
- Message: Street name and city information

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
- **Notifications**: Pushover API

### Data Flow
1. Script queries Waze API for alerts in specified bounds
2. Filters for police alerts only
3. Converts coordinates to street names via geocoding
4. Sends notifications to all configured Pushover users
5. Waits for specified interval before next check

### Error Handling
- Network errors are logged and retried
- Invalid responses are logged with details
- Geocoding failures fall back to "Unknown Street"
- Main loop continues running despite individual errors

## Troubleshooting

### Common Issues

**No notifications received:**
- Verify Pushover API key and user keys are correct
- Check internet connectivity
- Test with `--dry-run` to verify monitoring works

**No alerts found:**
- Verify geographic bounds are correct
- Check if monitoring area has active police alerts
- Try expanding the monitoring area

**Geocoding errors:**
- Nominatim has rate limits, errors are normal
- Script falls back to "Unknown Street" when geocoding fails

**Network errors:**
- Check internet connection
- Waze API may be temporarily unavailable
- Script will retry automatically

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

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool.

## License

This project is provided as-is for educational purposes. Use at your own risk and in accordance with applicable laws and terms of service. 