"""Kinesis event emitter for the observability logger.

This module is responsible for sending observability events to AWS Kinesis.
It defines the `KinesisEmitter` class, which handles AWS client
initialization, event serialization, and robust error handling.

The primary design principle is to "fail silently," ensuring that observability
instrumentation does not interfere with the application's core functionality.
If an event fails to send, the error is logged, and the operation returns
`False`, but no exceptions are raised.
"""

import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import threading

from ..config.settings import get_config
from ..models.events import ObservabilityEvent

logger = logging.getLogger(__name__)


class KinesisEmitter:
    """Handles the transmission of observability events to an AWS Kinesis stream.

    This class manages the lifecycle of the `boto3` Kinesis client, serializes
    events into the required format, and sends them to the configured stream.
    It is designed for internal use by the logger's components.

    The emitter also verifies access to the Kinesis stream in a background thread
    to warn the user of permission or accessibility issues without blocking the
    main application flow.

    Attributes:
        _config: The application's configuration settings.
        _client: The `boto3` Kinesis client instance.
        _stream_accessible: Boolean flag indicating if the Kinesis stream is accessible.
    """

    def __init__(self) -> None:
        """Initializes the KinesisEmitter.

        The emitter loads its configuration from the environment and immediately
        attempts to initialize the `boto3` Kinesis client. AWS credentials are
        sourced via the standard `boto3` credential chain.

        Additionally, verifies access to the configured Kinesis stream in a
        background thread to avoid blocking the main application flow.
        """
        self._config = get_config()
        self._client: Optional[Any] = None
        self._stream_accessible: bool = True  # Assume accessible by default
        self._initialize_client()
        # Verify stream access in background thread (non-blocking)
        self._verify_stream_access_async()

    def _initialize_client(self) -> None:
        """Initializes the `boto3` Kinesis client.

        This method attempts to create a Kinesis client using the configured
        AWS region. If initialization fails (e.g., due to missing credentials
        or permissions), the error is logged, and the client is set to `None`.
        This prevents further attempts to use the client.
        """
        try:
            self._client = boto3.client(
                "kinesis", region_name=self._config.aws_region
            )
            logger.debug(
                f"Initialized Kinesis client for region {self._config.aws_region}"
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize Kinesis client: {e}. "
                "Events will not be sent."
            )
            self._client = None

    def _verify_stream_access(self) -> bool:
        """Verifies access to the configured Kinesis stream.

        This method attempts to describe the stream to verify that:
        1. The stream exists
        2. The current AWS credentials have permission to access it

        Returns:
            True if stream is accessible, False otherwise.
        """
        if self._client is None:
            return False

        try:
            self._client.describe_stream(StreamName=self._config.kinesis_stream_name)
            logger.info(
                f"✓ Verified access to Kinesis stream: {self._config.kinesis_stream_name}"
            )
            return True
        except (BotoCoreError, ClientError) as e:
            # Extract error code from AWS response
            error_code = "UnknownError"
            error_message = str(e)

            if hasattr(e, "response") and e.response:
                error_code = e.response.get("Error", {}).get("Code", "UnknownError")

            # Provide specific error messages based on error type
            if error_code == "ResourceNotFoundException":
                logger.error(
                    f"✗ ALERTA: El stream de Kinesis '{self._config.kinesis_stream_name}' NO EXISTE. "
                    f"Error: {error_code}. Verifica que el nombre del stream sea correcto."
                )
            elif error_code in ["AccessDenied", "UnauthorizedOperation", "InvalidAction"]:
                logger.error(
                    f"✗ ALERTA: NO TIENES PERMISOS para acceder al stream de Kinesis '{self._config.kinesis_stream_name}'. "
                    f"Error: {error_code}. Verifica que las credenciales AWS tengan permiso 'kinesis:DescribeStream'."
                )
            else:
                logger.error(
                    f"✗ ALERTA: Error al verificar acceso al stream de Kinesis '{self._config.kinesis_stream_name}'. "
                    f"Error: {error_code} - {error_message}. "
                    f"Los eventos pueden no ser enviados correctamente."
                )
            return False
        except Exception as e:
            logger.error(
                f"✗ ALERTA: Error inesperado verificando acceso a Kinesis: {e}. "
                f"Los eventos pueden no ser enviados correctamente."
            )
            return False

    def _verify_stream_access_async(self) -> None:
        """Verifies Kinesis stream access in a background thread.

        This method launches a daemon thread to verify stream access without
        blocking the main application flow. The verification result is stored
        in `_stream_accessible` for informational purposes but does not affect
        event emission behavior (which remains non-blocking).
        """
        def verify():
            self._stream_accessible = self._verify_stream_access()

        # Create a daemon thread so it doesn't block application shutdown
        thread = threading.Thread(target=verify, daemon=True)
        thread.start()

    def emit(self, event: ObservabilityEvent) -> bool:
        """Emits a single observability event to the Kinesis stream.

        The event is first serialized to a JSON string. It is then encoded
        to UTF-8 bytes and sent to Kinesis using a `put_record` call. The
        `trace_id` of the event is used as the partition key to ensure that
        all events for a given trace are processed in order by the consumer.

        Args:
            event: The `ObservabilityEvent` to emit.

        Returns:
            True if the event was successfully sent, False otherwise.
        """
        if self._client is None:
            logger.warning(
                "Kinesis client not initialized. Dropping event: %s",
                event.event_type,
            )
            return False

        try:
            event_json = event.model_dump_json()

            response = self._client.put_record(
                StreamName=self._config.kinesis_stream_name,
                Data=event_json.encode("utf-8"),
                PartitionKey=event.trace_id,
            )

            logger.debug(
                "Emitted %s event for trace %s. Sequence: %s",
                event.event_type,
                event.trace_id,
                response.get("SequenceNumber", "unknown"),
            )
            return True

        except (BotoCoreError, ClientError) as e:
            # Extract error code from AWS response
            error_code = "UnknownError"
            if hasattr(e, "response") and e.response:
                error_code = e.response.get("Error", {}).get("Code", "UnknownError")

            # Provide specific error messages based on error type
            if error_code == "ResourceNotFoundException":
                logger.error(
                    f"✗ Error emitiendo evento {event.event_type}: Stream '{self._config.kinesis_stream_name}' NO EXISTE. "
                    f"Verifica el nombre del stream en la configuración."
                )
            elif error_code in ["AccessDenied", "UnauthorizedOperation", "InvalidAction"]:
                logger.error(
                    f"✗ Error emitiendo evento {event.event_type}: SIN PERMISOS para enviar a Kinesis. "
                    f"Verifica que las credenciales tengan permiso 'kinesis:PutRecord'."
                )
            else:
                logger.error(
                    f"✗ Error AWS emitiendo evento {event.event_type}: {error_code} - {e}. "
                    f"Evento descartado."
                )
            return False
        except Exception as e:
            logger.error(
                f"✗ Error inesperado emitiendo evento {event.event_type}: {e}. "
                f"Evento descartado."
            )
            return False

    def emit_dict(self, event_dict: Dict[str, Any]) -> bool:
        """Emits an event from a dictionary, bypassing Pydantic validation.

        This method is primarily intended for testing purposes where sending a
        raw dictionary is more convenient than constructing a full
        `ObservabilityEvent` object.

        Args:
            event_dict: A dictionary that conforms to the
                `ObservabilityEvent` schema.

        Returns:
            True if the event was successfully created and sent, False otherwise.
        """
        try:
            event = ObservabilityEvent(**event_dict)
            return self.emit(event)
        except Exception as e:
            logger.error("Failed to create event from dict: %s", e)
            return False


# The global emitter instance is managed as a singleton.
_emitter: Optional[KinesisEmitter] = None


def get_emitter() -> KinesisEmitter:
    """Provides access to the global `KinesisEmitter` singleton instance.

    This function ensures that only one `KinesisEmitter` is created per
    process, allowing the underlying `boto3` client and its connections to be
    reused across all trace and node operations. The emitter is initialized

    lazily on its first access.

    Returns:
        The singleton `KinesisEmitter` instance.
    """
    global _emitter
    if _emitter is None:
        _emitter = KinesisEmitter()
    return _emitter


def reset_emitter() -> None:
    """Resets the global emitter instance.

    This function is used exclusively for testing to ensure that tests can
    run in isolation without sharing an emitter state.
    """
    global _emitter
    _emitter = None
