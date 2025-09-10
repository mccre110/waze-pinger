import os
import pickle
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


class AlertCache:
    """Manages a persistent cache of seen alerts to prevent duplicates"""

    def __init__(self, cache_file: str = "alert_cache.pkl", duration_hours: int = None):
        self.cache_file = Path(cache_file)
        self.duration_hours = duration_hours or int(
            os.getenv("CACHE_DURATION_HOURS", "24")
        )
        self.seen_alerts: Dict[str, datetime] = {}
        self.load_cache()

    def load_cache(self):
        """Load the cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "rb") as f:
                    self.seen_alerts = pickle.load(f)
                logger.info(f"Loaded {len(self.seen_alerts)} alerts from cache")
                self.cleanup_expired()
            else:
                logger.info("No existing cache file found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self.seen_alerts = {}

    def save_cache(self):
        """Save the cache to disk"""
        try:
            with open(self.cache_file, "wb") as f:
                pickle.dump(self.seen_alerts, f)
            logger.debug(f"Saved {len(self.seen_alerts)} alerts to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")

    def cleanup_expired(self):
        """Remove expired alerts from cache"""
        cutoff_time = datetime.now() - timedelta(hours=self.duration_hours)
        before_count = len(self.seen_alerts)

        # Remove expired entries
        expired_uuids = [
            uuid
            for uuid, timestamp in self.seen_alerts.items()
            if timestamp < cutoff_time
        ]

        for uuid in expired_uuids:
            del self.seen_alerts[uuid]

        removed_count = before_count - len(self.seen_alerts)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired alerts from cache")

    def is_seen(self, alert_uuid: str) -> bool:
        """Check if an alert has been seen before"""
        return alert_uuid in self.seen_alerts

    def mark_seen(self, alert_uuid: str):
        """Mark an alert as seen"""
        self.seen_alerts[alert_uuid] = datetime.now()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "total_alerts": len(self.seen_alerts),
            "cache_duration_hours": self.duration_hours,
        }
