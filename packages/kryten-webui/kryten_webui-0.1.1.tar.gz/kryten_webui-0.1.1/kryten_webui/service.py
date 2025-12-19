"""Main service class for kryten-webui."""

import asyncio
import logging
from pathlib import Path

from kryten import KrytenClient

from kryten_webui.config import Config


logger = logging.getLogger(__name__)


class WebUIService:
    """Kryten WebUI Service."""

    def __init__(self, config_path: Path):
        """Initialize the service."""
        self.config = Config(config_path)
        self.client = KrytenClient(
            nats_url=self.config.nats_url,
            subject_prefix=self.config.nats_subject_prefix,
            service_name=self.config.service_name,
        )
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the service."""
        logger.info("Starting webui service")

        # Connect to NATS
        await self.client.connect()

        # Subscribe to events for dashboard updates
        await self.client.subscribe("chatMsg", self._handle_chat_message)
        await self.client.subscribe("usercount", self._handle_usercount)
        await self.client.subscribe("playlist", self._handle_playlist)

        logger.info("WebUI service started")

    async def stop(self) -> None:
        """Stop the service."""
        logger.info("Stopping webui service")
        self._shutdown_event.set()

        # Disconnect from NATS
        await self.client.disconnect()

        logger.info("WebUI service stopped")

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()

    async def _handle_chat_message(self, subject: str, data: dict) -> None:
        """Handle chatMsg events for dashboard display."""
        username = data.get("username", "unknown")
        msg = data.get("msg", "")
        logger.info(f"Chat message from {username}: {msg}")

        # TODO: Add web dashboard logic here
        # - Update chat display on dashboard
        # - Track chat activity
        # - Broadcast to websocket clients

    async def _handle_usercount(self, subject: str, data: dict) -> None:
        """Handle usercount events."""
        count = data.get("count", 0)
        logger.info(f"User count: {count}")

        # TODO: Add usercount display logic here
        # - Update dashboard metrics
        # - Broadcast to websocket clients

    async def _handle_playlist(self, subject: str, data: dict) -> None:
        """Handle playlist events."""
        logger.info("Playlist update received")

        # TODO: Add playlist display logic here
        # - Update playlist view on dashboard
        # - Track playlist state
        # - Broadcast to websocket clients
