import os
import aiohttp
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class NotificationProvider:
    """Handles sending notifications to users via Pushover and Discord webhooks"""

    def __init__(self):
        # Pushover configuration
        self.pushover_api_key = os.getenv("PUSHOVER_API_KEY")
        self.pushover_user_keys = (
            os.getenv("PUSHOVER_USER_KEYS").split(",")
            if os.getenv("PUSHOVER_USER_KEYS")
            else []
        )

        # Discord webhook configuration
        self.discord_webhook_urls = (
            os.getenv("DISCORD_WEBHOOK_URLS").split(",")
            if os.getenv("DISCORD_WEBHOOK_URLS")
            else []
        )

    async def notify_all_users(self, message: str):
        """Send notification to all configured users via all available channels"""
        # Send via Pushover
        for user_key in self.pushover_user_keys:
            await self.send_pushover_notification(message, user_key)

        # Send via Discord webhooks
        for webhook_url in self.discord_webhook_urls:
            await self.send_discord_notification(message, webhook_url)

    async def send_pushover_notification(self, message: str, user_key: str):
        """Send a notification to a specific user via Pushover"""
        logger.info(f"Pushover ({user_key}) Sending notification")
        try:
            pushover_url = "https://api.pushover.net/1/messages.json"
            data = {
                "token": self.pushover_api_key,
                "user": user_key,
                "message": message,
                "title": "Police Alert Nearby",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(pushover_url, data=data) as response:
                    if response.status == 200:
                        logger.info(
                            f"Pushover ({user_key}) Notification sent: {message}"
                        )
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Pushover ({user_key}) Failed to send notification: HTTP {response.status} - {error_text}"
                        )

        except Exception as e:
            logger.error(f"Pushover ({user_key}) Failed to send notification: {e}")

    async def send_discord_notification(self, message: str, webhook_url: str):
        """Send a notification via Discord webhook"""
        logger.info(f"Discord webhook sending notification")
        try:
            # Create Discord embed for better formatting
            embed = {
                "title": "🚨 Police Alert Nearby",
                "description": message,
                "color": 0xFF0000,  # Red color
                "timestamp": None,  # Will be set by Discord
                "footer": {"text": "Waze Pinger Alert System"},
            }

            payload = {
                "embeds": [embed],
                "username": "Waze Pinger",
                "avatar_url": "https://cdn-icons-png.flaticon.com/512/124/124010.png",  # Waze-like icon
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status in [200, 204]:
                        logger.info(f"Discord webhook notification sent: {message}")
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Discord webhook failed to send notification: HTTP {response.status} - {error_text}"
                        )

        except Exception as e:
            logger.error(f"Discord webhook failed to send notification: {e}")

    def get_configured_users(self) -> List[str]:
        """Get list of configured Pushover user keys"""
        return self.pushover_user_keys.copy()

    def get_configured_webhooks(self) -> List[str]:
        """Get list of configured Discord webhook URLs"""
        return self.discord_webhook_urls.copy()

    def is_configured(self) -> bool:
        """Check if notification provider is properly configured"""
        pushover_configured = bool(self.pushover_api_key and self.pushover_user_keys)
        discord_configured = bool(self.discord_webhook_urls)
        return pushover_configured or discord_configured

    def is_pushover_configured(self) -> bool:
        """Check if Pushover is properly configured"""
        return bool(self.pushover_api_key and self.pushover_user_keys)

    def is_discord_configured(self) -> bool:
        """Check if Discord webhooks are properly configured"""
        return bool(self.discord_webhook_urls)
