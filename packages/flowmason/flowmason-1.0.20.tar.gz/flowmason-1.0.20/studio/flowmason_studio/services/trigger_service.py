"""
Event Trigger Service.

Manages event watchers and triggers pipeline executions.
"""

import asyncio
import fnmatch
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from flowmason_studio.models.triggers import (
    EventTrigger,
    FileWatchConfig,
    FileWatchEvent,
    MCPEventConfig,
    MessageQueueConfig,
    PipelineCompletedConfig,
    TriggerEvent,
    TriggerStatus,
    TriggerType,
)
from flowmason_studio.services.trigger_storage import (
    TriggerStorage,
    get_trigger_storage,
)

logger = logging.getLogger(__name__)


class TriggerService:
    """Service for managing event triggers."""

    def __init__(
        self,
        storage: Optional[TriggerStorage] = None,
        execute_callback: Optional[Callable] = None,
    ):
        """Initialize the trigger service.

        Args:
            storage: Trigger storage instance
            execute_callback: Callback to execute pipelines
                Signature: async def execute(pipeline_id, inputs) -> run_id
        """
        self.storage = storage or get_trigger_storage()
        self.execute_callback = execute_callback

        # Active watchers
        self._file_watchers: Dict[str, asyncio.Task] = {}
        self._mcp_listeners: Dict[str, asyncio.Task] = {}
        self._queue_consumers: Dict[str, asyncio.Task] = {}
        self._running = False

        # Event subscriptions for pipeline completion triggers
        self._completion_triggers: Dict[str, List[str]] = {}  # pipeline_id -> trigger_ids

        # Debounce tracking for file watchers
        self._file_debounce: Dict[str, asyncio.Task] = {}

    async def start(self) -> None:
        """Start the trigger service."""
        if self._running:
            return

        self._running = True
        logger.info("Starting trigger service")

        # Load and start all active triggers
        await self._initialize_triggers()

    async def stop(self) -> None:
        """Stop the trigger service."""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping trigger service")

        # Cancel all watchers
        for task in self._file_watchers.values():
            task.cancel()
        for task in self._mcp_listeners.values():
            task.cancel()
        for task in self._queue_consumers.values():
            task.cancel()

        self._file_watchers.clear()
        self._mcp_listeners.clear()
        self._queue_consumers.clear()
        self._completion_triggers.clear()

    async def _initialize_triggers(self) -> None:
        """Initialize all active triggers."""
        # File watchers
        file_triggers = self.storage.get_active_triggers_by_type(TriggerType.FILE_WATCH)
        for trigger in file_triggers:
            await self._start_file_watcher(trigger)

        # Pipeline completion triggers
        completion_triggers = self.storage.get_active_triggers_by_type(
            TriggerType.PIPELINE_COMPLETED
        )
        for trigger in completion_triggers:
            self._register_completion_trigger(trigger)

        # MCP event listeners
        mcp_triggers = self.storage.get_active_triggers_by_type(TriggerType.MCP_EVENT)
        for trigger in mcp_triggers:
            await self._start_mcp_listener(trigger)

        # Message queue consumers
        queue_triggers = self.storage.get_active_triggers_by_type(
            TriggerType.MESSAGE_QUEUE
        )
        for trigger in queue_triggers:
            await self._start_queue_consumer(trigger)

        logger.info(
            f"Initialized {len(file_triggers)} file watchers, "
            f"{len(completion_triggers)} completion triggers, "
            f"{len(mcp_triggers)} MCP listeners, "
            f"{len(queue_triggers)} queue consumers"
        )

    # File Watch Triggers

    async def _start_file_watcher(self, trigger: EventTrigger) -> None:
        """Start a file watcher for a trigger."""
        try:
            config = FileWatchConfig(**trigger.config)
            task = asyncio.create_task(
                self._watch_files(trigger.id, config)
            )
            self._file_watchers[trigger.id] = task
            logger.info(f"Started file watcher for trigger {trigger.id}: {config.path}")
        except Exception as e:
            logger.error(f"Failed to start file watcher for {trigger.id}: {e}")
            self.storage.update_trigger_status(
                trigger.id, TriggerStatus.ERROR, str(e)
            )

    async def _watch_files(
        self,
        trigger_id: str,
        config: FileWatchConfig,
    ) -> None:
        """Watch files and trigger on changes."""
        # Simple polling-based watcher
        # In production, use watchdog library for efficient native events

        path = Path(config.path)
        base_dir = path.parent
        pattern = path.name

        # Track file states
        file_states: Dict[str, float] = {}  # path -> mtime

        # Initialize file states
        if base_dir.exists():
            for file_path in base_dir.glob(pattern if not config.recursive else f"**/{pattern}"):
                if file_path.is_file():
                    file_states[str(file_path)] = file_path.stat().st_mtime

        while self._running:
            try:
                await asyncio.sleep(1)  # Poll interval

                trigger = self.storage.get_trigger(trigger_id)
                if not trigger or not trigger.enabled:
                    break

                if not base_dir.exists():
                    continue

                current_files: Set[str] = set()
                glob_pattern = pattern if not config.recursive else f"**/{pattern}"

                for file_path in base_dir.glob(glob_pattern):
                    if not file_path.is_file():
                        continue

                    file_str = str(file_path)
                    current_files.add(file_str)

                    # Check ignore patterns
                    if any(fnmatch.fnmatch(file_path.name, p) for p in config.ignore_patterns):
                        continue

                    mtime = file_path.stat().st_mtime

                    # Check for new files
                    if file_str not in file_states:
                        if FileWatchEvent.CREATED in config.events:
                            await self._debounced_file_trigger(
                                trigger_id, file_str, "created",
                                config.debounce_seconds
                            )
                        file_states[file_str] = mtime
                    # Check for modified files
                    elif mtime > file_states[file_str]:
                        if FileWatchEvent.MODIFIED in config.events:
                            await self._debounced_file_trigger(
                                trigger_id, file_str, "modified",
                                config.debounce_seconds
                            )
                        file_states[file_str] = mtime

                # Check for deleted files
                if FileWatchEvent.DELETED in config.events:
                    deleted = set(file_states.keys()) - current_files
                    for file_str in deleted:
                        await self._fire_trigger(
                            trigger_id,
                            "file_deleted",
                            {"path": file_str, "event": "deleted"}
                        )
                        del file_states[file_str]

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"File watcher error for {trigger_id}: {e}")
                await asyncio.sleep(5)

    async def _debounced_file_trigger(
        self,
        trigger_id: str,
        file_path: str,
        event: str,
        debounce_seconds: float,
    ) -> None:
        """Fire a file trigger with debouncing."""
        key = f"{trigger_id}:{file_path}"

        # Cancel existing debounce timer
        if key in self._file_debounce:
            self._file_debounce[key].cancel()

        async def delayed_fire() -> None:
            await asyncio.sleep(debounce_seconds)
            await self._fire_trigger(
                trigger_id,
                f"file_{event}",
                {"path": file_path, "event": event}
            )
            del self._file_debounce[key]

        self._file_debounce[key] = asyncio.create_task(delayed_fire())

    # Pipeline Completion Triggers

    def _register_completion_trigger(self, trigger: EventTrigger) -> None:
        """Register a pipeline completion trigger."""
        try:
            config = PipelineCompletedConfig(**trigger.config)
            source_id = config.source_pipeline_id

            if source_id not in self._completion_triggers:
                self._completion_triggers[source_id] = []

            self._completion_triggers[source_id].append(trigger.id)
            logger.info(
                f"Registered completion trigger {trigger.id} "
                f"for pipeline {source_id}"
            )
        except Exception as e:
            logger.error(f"Failed to register completion trigger {trigger.id}: {e}")
            self.storage.update_trigger_status(
                trigger.id, TriggerStatus.ERROR, str(e)
            )

    async def notify_pipeline_completed(
        self,
        pipeline_id: str,
        run_id: str,
        status: str,
        outputs: Dict[str, Any],
    ) -> None:
        """Notify that a pipeline has completed."""
        if pipeline_id not in self._completion_triggers:
            return

        for trigger_id in self._completion_triggers[pipeline_id]:
            trigger = self.storage.get_trigger(trigger_id)
            if not trigger or not trigger.enabled:
                continue

            try:
                config = PipelineCompletedConfig(**trigger.config)

                # Check if status matches
                if config.status.value == "any" or config.status.value == status:
                    event_data: Dict[str, Any] = {
                        "source_pipeline_id": pipeline_id,
                        "source_run_id": run_id,
                        "status": status,
                    }

                    # Add outputs if configured
                    if config.pass_outputs:
                        event_data["outputs"] = outputs

                    await self._fire_trigger(
                        trigger_id,
                        "pipeline_completed",
                        event_data
                    )
            except Exception as e:
                logger.error(f"Completion trigger {trigger_id} failed: {e}")

    # MCP Event Triggers

    async def _start_mcp_listener(self, trigger: EventTrigger) -> None:
        """Start an MCP event listener."""
        try:
            config = MCPEventConfig(**trigger.config)
            task = asyncio.create_task(
                self._listen_mcp_events(trigger.id, config)
            )
            self._mcp_listeners[trigger.id] = task
            logger.info(
                f"Started MCP listener for trigger {trigger.id}: "
                f"{config.server_name}/{config.event_type}"
            )
        except Exception as e:
            logger.error(f"Failed to start MCP listener for {trigger.id}: {e}")
            self.storage.update_trigger_status(
                trigger.id, TriggerStatus.ERROR, str(e)
            )

    async def _listen_mcp_events(
        self,
        trigger_id: str,
        config: MCPEventConfig,
    ) -> None:
        """Listen for MCP events."""
        # This would integrate with the MCP server
        # For now, this is a placeholder that can be extended
        while self._running:
            try:
                await asyncio.sleep(60)  # Placeholder
                trigger = self.storage.get_trigger(trigger_id)
                if not trigger or not trigger.enabled:
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"MCP listener error for {trigger_id}: {e}")
                await asyncio.sleep(5)

    async def emit_mcp_event(
        self,
        server_name: str,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Emit an MCP event to trigger listeners."""
        triggers = self.storage.get_active_triggers_by_type(TriggerType.MCP_EVENT)

        for trigger in triggers:
            try:
                config = MCPEventConfig(**trigger.config)

                if config.server_name != server_name:
                    continue
                if config.event_type != event_type:
                    continue

                # Check filter
                if config.filter:
                    if not self._matches_filter(event_data, config.filter):
                        continue

                await self._fire_trigger(
                    trigger.id,
                    f"mcp_{event_type}",
                    event_data
                )
            except Exception as e:
                logger.error(f"MCP event trigger {trigger.id} failed: {e}")

    def _matches_filter(
        self,
        data: Dict[str, Any],
        filter_spec: Dict[str, Any],
    ) -> bool:
        """Check if data matches a filter specification."""
        for key, expected in filter_spec.items():
            value = data.get(key)
            if isinstance(expected, dict):
                if not isinstance(value, dict):
                    return False
                if not self._matches_filter(value, expected):
                    return False
            elif value != expected:
                return False
        return True

    # Message Queue Triggers

    async def _start_queue_consumer(self, trigger: EventTrigger) -> None:
        """Start a message queue consumer."""
        try:
            config = MessageQueueConfig(**trigger.config)
            task = asyncio.create_task(
                self._consume_queue(trigger.id, config)
            )
            self._queue_consumers[trigger.id] = task
            logger.info(
                f"Started queue consumer for trigger {trigger.id}: "
                f"{config.queue_type}/{config.queue_name}"
            )
        except Exception as e:
            logger.error(f"Failed to start queue consumer for {trigger.id}: {e}")
            self.storage.update_trigger_status(
                trigger.id, TriggerStatus.ERROR, str(e)
            )

    async def _consume_queue(
        self,
        trigger_id: str,
        config: MessageQueueConfig,
    ) -> None:
        """Consume messages from a queue."""
        # This would integrate with actual message queue libraries
        # (redis, aio-pika, aiokafka, etc.)
        # For now, this is a placeholder

        while self._running:
            try:
                await asyncio.sleep(60)  # Placeholder
                trigger = self.storage.get_trigger(trigger_id)
                if not trigger or not trigger.enabled:
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue consumer error for {trigger_id}: {e}")
                await asyncio.sleep(5)

    # Core Trigger Firing

    async def _fire_trigger(
        self,
        trigger_id: str,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> Optional[TriggerEvent]:
        """Fire a trigger and execute the associated pipeline."""
        trigger = self.storage.get_trigger(trigger_id)
        if not trigger:
            logger.warning(f"Trigger {trigger_id} not found")
            return None

        if not trigger.enabled:
            logger.debug(f"Trigger {trigger_id} is disabled")
            return None

        if not self.storage.can_trigger(trigger_id):
            logger.debug(f"Trigger {trigger_id} in cooldown")
            return None

        # Resolve inputs
        resolved_inputs = self._resolve_inputs(trigger, event_data)

        # Create event record
        event = self.storage.create_event(
            trigger_id=trigger_id,
            pipeline_id=trigger.pipeline_id,
            event_type=event_type,
            event_data=event_data,
            resolved_inputs=resolved_inputs,
        )

        # Update trigger stats
        self.storage.record_trigger_fired(trigger_id)

        # Execute pipeline
        if self.execute_callback:
            try:
                self.storage.update_event(
                    event.id,
                    status="executing",
                    started_at=datetime.utcnow()
                )

                run_id = await self.execute_callback(
                    trigger.pipeline_id,
                    resolved_inputs
                )

                self.storage.update_event(
                    event.id,
                    status="completed",
                    run_id=run_id,
                    completed_at=datetime.utcnow()
                )

                logger.info(
                    f"Trigger {trigger_id} fired: pipeline={trigger.pipeline_id}, "
                    f"run={run_id}"
                )
            except Exception as e:
                logger.error(f"Trigger execution failed for {trigger_id}: {e}")
                self.storage.update_event(
                    event.id,
                    status="failed",
                    error_message=str(e),
                    completed_at=datetime.utcnow()
                )
        else:
            # No callback - just log
            logger.info(f"Trigger {trigger_id} fired (no executor configured)")
            self.storage.update_event(
                event.id,
                status="completed",
                completed_at=datetime.utcnow()
            )

        return event

    def _resolve_inputs(
        self,
        trigger: EventTrigger,
        event_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve pipeline inputs from trigger config and event data."""
        inputs = dict(trigger.default_inputs)

        # Get input mapping from config
        config = trigger.config
        input_mapping = config.get("input_mapping", {})
        output_mapping = config.get("output_mapping", {})

        # Apply input mapping (JSONPath-like)
        for target_key, source_path in input_mapping.items():
            value = self._extract_value(event_data, source_path)
            if value is not None:
                inputs[target_key] = value

        # Apply output mapping for pipeline completion triggers
        if trigger.trigger_type == TriggerType.PIPELINE_COMPLETED:
            outputs = event_data.get("outputs", {})
            for target_key, source_key in output_mapping.items():
                if source_key in outputs:
                    inputs[target_key] = outputs[source_key]
            # If pass_outputs and no mapping, pass all outputs
            if config.get("pass_outputs") and not output_mapping:
                inputs.update(outputs)

        # Add event metadata
        inputs["_trigger_event"] = {
            "trigger_id": trigger.id,
            "event_type": event_data.get("event", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return inputs

    def _extract_value(
        self,
        data: Dict[str, Any],
        path: str,
    ) -> Any:
        """Extract a value from data using a path expression."""
        # Simple path extraction ($.key.subkey)
        if path.startswith("$."):
            path = path[2:]

        parts = path.split(".")
        current: Any = data

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    idx = int(part)
                    current = current[idx]
                except (ValueError, IndexError):
                    return None
            else:
                return None

            if current is None:
                return None

        return current

    # Trigger Management

    async def add_trigger(self, trigger: EventTrigger) -> None:
        """Add and start a new trigger."""
        if trigger.trigger_type == TriggerType.FILE_WATCH:
            await self._start_file_watcher(trigger)
        elif trigger.trigger_type == TriggerType.PIPELINE_COMPLETED:
            self._register_completion_trigger(trigger)
        elif trigger.trigger_type == TriggerType.MCP_EVENT:
            await self._start_mcp_listener(trigger)
        elif trigger.trigger_type == TriggerType.MESSAGE_QUEUE:
            await self._start_queue_consumer(trigger)

    async def remove_trigger(self, trigger_id: str) -> None:
        """Stop and remove a trigger."""
        # Stop file watcher
        if trigger_id in self._file_watchers:
            self._file_watchers[trigger_id].cancel()
            del self._file_watchers[trigger_id]

        # Stop MCP listener
        if trigger_id in self._mcp_listeners:
            self._mcp_listeners[trigger_id].cancel()
            del self._mcp_listeners[trigger_id]

        # Stop queue consumer
        if trigger_id in self._queue_consumers:
            self._queue_consumers[trigger_id].cancel()
            del self._queue_consumers[trigger_id]

        # Remove completion trigger
        for pipeline_id, trigger_ids in self._completion_triggers.items():
            if trigger_id in trigger_ids:
                trigger_ids.remove(trigger_id)

    async def pause_trigger(self, trigger_id: str) -> None:
        """Pause a trigger."""
        await self.remove_trigger(trigger_id)
        self.storage.update_trigger_status(trigger_id, TriggerStatus.PAUSED)

    async def resume_trigger(self, trigger_id: str) -> None:
        """Resume a paused trigger."""
        trigger = self.storage.get_trigger(trigger_id)
        if trigger:
            self.storage.update_trigger_status(trigger_id, TriggerStatus.ACTIVE)
            await self.add_trigger(trigger)

    # Custom Event Emission

    async def emit_custom_event(
        self,
        endpoint: str,
        event_data: Dict[str, Any],
    ) -> List[TriggerEvent]:
        """Emit a custom event."""
        triggers = self.storage.get_active_triggers_by_type(TriggerType.CUSTOM)
        events: List[TriggerEvent] = []

        for trigger in triggers:
            config = trigger.config
            if config.get("endpoint") != endpoint:
                continue

            # Check filter
            filter_spec = config.get("filter")
            if filter_spec and not self._matches_filter(event_data, filter_spec):
                continue

            event = await self._fire_trigger(
                trigger.id,
                f"custom_{endpoint}",
                event_data
            )
            if event:
                events.append(event)

        return events


# Global instance
_trigger_service: Optional[TriggerService] = None


def get_trigger_service() -> TriggerService:
    """Get the global trigger service instance."""
    global _trigger_service
    if _trigger_service is None:
        _trigger_service = TriggerService()
    return _trigger_service


async def start_trigger_service() -> None:
    """Start the trigger service."""
    service = get_trigger_service()
    await service.start()


async def stop_trigger_service() -> None:
    """Stop the trigger service."""
    service = get_trigger_service()
    await service.stop()
