"""NATS command handler for kryten-robot service.

Handles system commands on the kryten.robot.command subject, including:
- system.ping - Service discovery and health check
- system.health - Detailed health status
- system.stats - Service statistics
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from .nats_client import NatsClient


class RobotCommandHandler:
    """Handles system commands on kryten.robot.command subject."""

    def __init__(
        self,
        nats_client: NatsClient,
        logger: logging.Logger,
        version: str = "unknown",
        config: Any = None,
        connector: Any = None,
        publisher: Any = None,
        cmd_subscriber: Any = None,
    ):
        """Initialize robot command handler.

        Args:
            nats_client: NatsClient instance for NATS operations
            logger: Logger instance
            version: Service version string
            config: KrytenConfig for accessing health port etc
            connector: CytubeConnector for connection status
            publisher: EventPublisher for stats
            cmd_subscriber: CommandSubscriber for stats
        """
        self.nats = nats_client
        self.logger = logger
        self.version = version
        self.config = config
        self.connector = connector
        self.publisher = publisher
        self.cmd_subscriber = cmd_subscriber

        self._subscription = None
        self._commands_processed = 0

    async def start(self) -> None:
        """Subscribe to command subject."""
        subject = "kryten.robot.command"
        self._subscription = await self.nats.subscribe_request_reply(
            subject, self._handle_command
        )
        self.logger.info(f"Robot command handler subscribed to {subject}")

    async def stop(self) -> None:
        """Unsubscribe from command subject."""
        if self._subscription:
            await self.nats.unsubscribe(self._subscription)
            self._subscription = None
        self.logger.info("Robot command handler stopped")

    async def _handle_command(self, msg) -> None:
        """Handle incoming command messages.

        Args:
            msg: NATS message with .data and .reply
        """
        self._commands_processed += 1

        try:
            request = json.loads(msg.data.decode())
            command = request.get("command", "")

            if not command:
                await self._send_response(msg.reply, {
                    "service": "robot",
                    "success": False,
                    "error": "Missing 'command' field",
                })
                return

            # Check service routing
            service = request.get("service")
            if service and service not in ("robot", "system"):
                await self._send_response(msg.reply, {
                    "service": "robot",
                    "success": False,
                    "error": f"Command intended for '{service}', not 'robot'",
                })
                return

            # Dispatch command
            handlers = {
                "system.ping": self._handle_ping,
                "system.health": self._handle_health,
                "system.stats": self._handle_stats,
            }

            handler = handlers.get(command)
            if not handler:
                await self._send_response(msg.reply, {
                    "service": "robot",
                    "command": command,
                    "success": False,
                    "error": f"Unknown command: {command}",
                })
                return

            result = await handler(request)
            await self._send_response(msg.reply, {
                "service": "robot",
                "command": command,
                "success": True,
                "data": result,
            })

        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in command: {e}")
            await self._send_response(msg.reply, {
                "service": "robot",
                "success": False,
                "error": f"Invalid JSON: {e}",
            })
        except Exception as e:
            self.logger.error(f"Error handling command: {e}", exc_info=True)
            await self._send_response(msg.reply, {
                "service": "robot",
                "success": False,
                "error": str(e),
            })

    async def _send_response(self, reply_to: str | None, response: dict) -> None:
        """Send response to reply subject.

        Args:
            reply_to: Reply subject
            response: Response dict to send
        """
        if reply_to:
            try:
                data = json.dumps(response).encode()
                await self.nats.publish(reply_to, data)
            except Exception as e:
                self.logger.error(f"Failed to send response: {e}")

    async def _handle_ping(self, request: dict) -> dict:
        """Handle system.ping - Simple liveness check with metadata."""
        uptime_seconds = self._get_nats_uptime()

        result = {
            "pong": True,
            "service": "robot",
            "version": self.version,
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add metrics endpoint if health is enabled
        if self.config and self.config.health.enabled:
            result["metrics_endpoint"] = (
                f"http://{self.config.health.host}:{self.config.health.port}/health"
            )

        # Add CyTube connection info
        if self.connector:
            result["cytube_connected"] = self.connector.is_connected
            if self.connector.is_connected:
                result["channel"] = self.config.cytube.channel if self.config else "unknown"
                result["domain"] = self.config.cytube.domain if self.config else "unknown"

        return result

    async def _handle_health(self, request: dict) -> dict:
        """Handle system.health - Detailed health status."""
        uptime_seconds = self._get_nats_uptime()

        health = {
            "service": "robot",
            "status": "healthy",
            "version": self.version,
            "uptime_seconds": uptime_seconds,
        }

        # NATS status
        health["nats_connected"] = self.nats.is_connected
        health["nats_reconnect_count"] = self.nats.reconnect_count

        # CyTube status
        if self.connector:
            health["cytube_connected"] = self.connector.is_connected
            if self.config:
                health["channel"] = self.config.cytube.channel
                health["domain"] = self.config.cytube.domain

        # Metrics endpoint
        if self.config and self.config.health.enabled:
            health["metrics_endpoint"] = (
                f"http://{self.config.health.host}:{self.config.health.port}/health"
            )

        return health

    async def _handle_stats(self, request: dict) -> dict:
        """Handle system.stats - Service statistics."""
        uptime_seconds = self._get_nats_uptime()

        stats = {
            "service": "robot",
            "version": self.version,
            "uptime_seconds": uptime_seconds,
            "commands_processed": self._commands_processed,
        }

        # NATS stats
        nats_stats = self.nats.stats
        stats["messages_published"] = nats_stats.get("messages_published", 0)
        stats["bytes_sent"] = nats_stats.get("bytes_sent", 0)
        stats["nats_errors"] = nats_stats.get("errors", 0)

        # Event publisher stats
        if self.publisher:
            stats["events_published"] = getattr(self.publisher, "_event_count", 0)

        # Command subscriber stats
        if self.cmd_subscriber:
            cmd_stats = self.cmd_subscriber.stats
            stats["cytube_commands_processed"] = cmd_stats.get("commands_processed", 0)
            stats["cytube_commands_succeeded"] = cmd_stats.get("commands_succeeded", 0)
            stats["cytube_commands_failed"] = cmd_stats.get("commands_failed", 0)

        return stats

    def _get_nats_uptime(self) -> float:
        """Get NATS connection uptime in seconds."""
        if self.nats.connected_since:
            return time.time() - self.nats.connected_since
        return 0.0
