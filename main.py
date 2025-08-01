import os
import aiohttp
import asyncio
import json
import logging
from datetime import datetime
import typer
from typing import Optional
import folium
import webbrowser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("waze_monitor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = typer.Typer()

# Coordinates for LA County - pulled from environment variables
bounds = {
    "top": float(
        os.getenv("BOUNDS_TOP", "34.8233")
    ),  # Top Right latitude (northern LA County)
    "bottom": float(
        os.getenv("BOUNDS_BOTTOM", "32.5123")
    ),  # Bottom Right latitude (southern LA County)
    "left": float(
        os.getenv("BOUNDS_LEFT", "-119.2073")
    ),  # Bottom Left longitude (western LA County)
    "right": float(
        os.getenv("BOUNDS_RIGHT", "-117.6461")
    ),  # Top Right longitude (eastern LA County)
}

logger.info(f"Monitoring area: {bounds}")

PUSHOVER_API_KEY = os.getenv("PUSHOVER_API_KEY")
PUSHOVER_USER_KEYS = (
    os.getenv("PUSHOVER_USER_KEYS").split(",")
    if os.getenv("PUSHOVER_USER_KEYS")
    else []
)


async def get_street_name_from_coordinates(lat, lon):
    """Fetch street name from coordinates using OpenStreetMap Nominatim"""
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"

    headers = {"User-Agent": "WazePinger/1.0"}  # Required by Nominatim terms of service

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Check if there's an error in the response
                    if "error" in data:
                        logger.error(f"Geocoding error: {data['error']}")
                        return "Unknown Street"

                    address = data.get("address", {})

                    # Try to get the most specific street name
                    street_name = (
                        address.get("road")
                        or address.get("street")
                        or address.get("highway")
                        or "Unknown Street"
                    )

                    return street_name
                else:
                    logger.error(f"Geocoding failed: HTTP {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response body: {response_text}")
                    return "Unknown Street"
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return "Unknown Street"


async def check_waze_alerts(custom_bounds: Optional[dict] = None):
    # Use custom bounds if provided, otherwise use global bounds
    current_bounds = custom_bounds or bounds

    # Correct Waze API endpoint (working as of 2025)
    timestamp = int(asyncio.get_event_loop().time() * 1000)

    # Use the working API endpoint
    url = f"https://www.waze.com/live-map/api/georss?top={current_bounds['top']}&bottom={current_bounds['bottom']}&left={current_bounds['left']}&right={current_bounds['right']}&env=na&types=alerts,traffic,users&_={timestamp}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.waze.com/live-map",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "X-Requested-With": "XMLHttpRequest",
    }

    logger.info("Checking for Waze alerts...")
    logger.info(f"Requesting URL: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    alerts = data.get("alerts", [])
                    logger.info(f"✅ Success! Found {len(alerts)} total alerts")

                    police_alerts = [
                        alert for alert in alerts if alert.get("type") == "POLICE"
                    ]
                    logger.info(f"Found {len(police_alerts)} police alerts")

                    for alert in police_alerts:
                        description = alert.get("street", "Unknown location")
                        location = f"{alert.get('location', {}).get('y', 'N/A')}, {alert.get('location', {}).get('x', 'N/A')}"
                        city = alert.get("city", "Unknown city")

                        # Extract coordinates
                        lat = alert.get("location", {}).get("y")
                        lon = alert.get("location", {}).get("x")

                        # Get street name from coordinates
                        if lat and lon:
                            street_name = await get_street_name_from_coordinates(
                                lat, lon
                            )
                            logger.info(
                                f"Police alert: {description} at {street_name} ({location}) in {city}"
                            )
                            await notify_all_users(
                                f"Police alert on {street_name} in {city}"
                            )
                        else:
                            logger.info(
                                f"Police alert: {description} at {location} in {city}"
                            )
                            await notify_all_users(
                                f"Police alert on {description} in {city}"
                            )
                else:
                    logger.error(f"HTTP {response.status}: Failed to fetch Waze data")
                    logger.error(f"Response headers: {dict(response.headers)}")
                    response_text = await response.text()
                    logger.error(f"Response body: {response_text[:500]}...")

    except aiohttp.ClientError as e:
        logger.error(f"Network error: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


async def notify_all_users(msg):
    for user_key in PUSHOVER_USER_KEYS:
        await send_notification(msg, user_key)


async def send_notification(msg, user_key):
    logger.info(f"({user_key}) Sending notification")
    try:
        pushover_url = "https://api.pushover.net/1/messages.json"
        data = {
            "token": PUSHOVER_API_KEY,
            "user": user_key,
            "message": msg,
            "title": "Police Alert Nearby",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(pushover_url, data=data) as response:
                if response.status == 200:
                    logger.info(f"({user_key}) Notification sent: {msg}")
                else:
                    error_text = await response.text()
                    logger.error(
                        f"({user_key}) Failed to send notification: HTTP {response.status} - {error_text}"
                    )

    except Exception as e:
        logger.error(f"({user_key}) Failed to send notification: {e}")


async def monitor_loop(
    interval: int = 300, custom_bounds: Optional[dict] = None, dry_run: bool = False
):
    """Main monitoring loop"""
    logger.info("Starting Waze police alert monitor...")
    logger.info(f"Monitoring every {interval} seconds")

    if dry_run:
        logger.info("DRY RUN MODE: Notifications will not be sent")

    # Run every specified interval
    while True:
        try:
            await check_waze_alerts(custom_bounds)
            logger.info(f"Sleeping for {interval} seconds...")
            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying


@app.command()
def monitor(
    top: Optional[float] = typer.Option(None, "--top", "-t", help="Top latitude bound"),
    bottom: Optional[float] = typer.Option(
        None, "--bottom", "-b", help="Bottom latitude bound"
    ),
    left: Optional[float] = typer.Option(
        None, "--left", "-l", help="Left longitude bound"
    ),
    right: Optional[float] = typer.Option(
        None, "--right", "-r", help="Right longitude bound"
    ),
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Run without sending notifications"
    ),
):
    """Monitor Waze for police alerts in the specified area"""

    # Build custom bounds if any are provided
    custom_bounds = None
    if any([top, bottom, left, right]):
        custom_bounds = {
            "top": top or bounds["top"],
            "bottom": bottom or bounds["bottom"],
            "left": left or bounds["left"],
            "right": right or bounds["right"],
        }
        logger.info(f"Using custom bounds: {custom_bounds}")

    if dry_run:
        logger.info("DRY RUN MODE: Notifications will not be sent")

    # Run the monitoring loop
    asyncio.run(monitor_loop(interval, custom_bounds, dry_run))


@app.command()
def check_once(
    top: Optional[float] = typer.Option(None, "--top", "-t", help="Top latitude bound"),
    bottom: Optional[float] = typer.Option(
        None, "--bottom", "-b", help="Bottom latitude bound"
    ),
    left: Optional[float] = typer.Option(
        None, "--left", "-l", help="Left longitude bound"
    ),
    right: Optional[float] = typer.Option(
        None, "--right", "-r", help="Right longitude bound"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Run without sending notifications"
    ),
):
    """Check for police alerts once and exit"""

    # Build custom bounds if any are provided
    custom_bounds = None
    if any([top, bottom, left, right]):
        custom_bounds = {
            "top": top or bounds["top"],
            "bottom": bottom or bounds["bottom"],
            "left": left or bounds["left"],
            "right": right or bounds["right"],
        }
        logger.info(f"Using custom bounds: {custom_bounds}")

    if dry_run:
        logger.info("DRY RUN MODE: Notifications will not be sent")

    # Run a single check
    asyncio.run(check_waze_alerts(custom_bounds))


@app.command()
def show_bounds(
    open_browser: bool = typer.Option(
        False, "--open", "-o", help="Open map in browser automatically"
    ),
    save_path: Optional[str] = typer.Option(
        None, "--save", "-s", help="Save map to specific path"
    ),
):
    """Show the current monitoring bounds and optionally display on a map"""
    typer.echo(f"Current monitoring bounds:")
    typer.echo(f"  Top: {bounds['top']}")
    typer.echo(f"  Bottom: {bounds['bottom']}")
    typer.echo(f"  Left: {bounds['left']}")
    typer.echo(f"  Right: {bounds['right']}")

    # Calculate center point for the map
    center_lat = (bounds["top"] + bounds["bottom"]) / 2
    center_lon = (bounds["left"] + bounds["right"]) / 2

    # Create a map centered on the monitoring area
    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=10, tiles="OpenStreetMap"
    )

    # Add a rectangle showing the monitoring bounds
    bounds_coords = [
        [bounds["bottom"], bounds["left"]],  # Southwest
        [bounds["top"], bounds["right"]],  # Northeast
    ]

    folium.Rectangle(
        bounds=bounds_coords,
        color="red",
        weight=2,
        fill=True,
        fillColor="red",
        fillOpacity=0.2,
        popup="Monitoring Area",
    ).add_to(m)

    # Add markers for the corners
    folium.Marker(
        [bounds["top"], bounds["right"]],
        popup="Top Right",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    folium.Marker(
        [bounds["bottom"], bounds["left"]],
        popup="Bottom Left",
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

    # Add a center marker
    folium.Marker(
        [center_lat, center_lon],
        popup="Center of Monitoring Area",
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)

    # Determine save path
    if save_path:
        map_path = Path(save_path)
    else:
        map_path = Path("monitoring_bounds.html")

    # Save the map
    m.save(str(map_path))
    typer.echo(f"Map saved to: {map_path.absolute()}")

    if open_browser:
        typer.echo("Opening map in browser...")
        webbrowser.open(f"file://{map_path.absolute()}")
    else:
        typer.echo(f"To view the map, open: {map_path.absolute()}")
        typer.echo("Or use: --open to automatically open in browser")


if __name__ == "__main__":
    app()
