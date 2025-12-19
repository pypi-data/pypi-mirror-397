"""Main service class for kryten-bingo."""

import asyncio
import logging
from pathlib import Path

from kryten import KrytenClient

from kryten_bingo.config import Config


logger = logging.getLogger(__name__)


class BingoService:
    """Kryten Bingo Service."""

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
        logger.info("Starting bingo service")

        # Connect to NATS
        await self.client.connect()

        # Subscribe to events
        await self.client.subscribe("chatMsg", self._handle_chat_message)

        logger.info("Bingo service started")

    async def stop(self) -> None:
        """Stop the service."""
        logger.info("Stopping bingo service")
        self._shutdown_event.set()

        # Disconnect from NATS
        await self.client.disconnect()

        logger.info("Bingo service stopped")

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()

    async def _handle_chat_message(self, subject: str, data: dict) -> None:
        """Handle chatMsg events."""
        username = data.get("username", "unknown")
        msg = data.get("msg", "")
        logger.info(f"Chat message from {username}: {msg}")

        # TODO: Add bingo game logic here
        # - Detect bingo commands (!bingo, !card, etc.)
        # - Track player cards
        # - Check for bingo wins
        # - Manage game state
