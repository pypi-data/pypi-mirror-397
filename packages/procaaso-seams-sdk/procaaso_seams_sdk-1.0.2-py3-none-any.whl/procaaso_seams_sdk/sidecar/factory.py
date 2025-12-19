"""
Factory functions for convenient sidecar setup.

Provides high-level API to eliminate boilerplate when connecting
actuator services to sidecar ENS.
"""

import logging
from typing import Any, Optional, Type

from ..bus.polling_router import PollingBusRouter
from ..services.actuator import ActuatorService
from .adapter import SidecarBusAdapter
from .store import RemoteSeamStore


async def connect_actuator(
    sidecar_url: str,
    system_name: str,
    component_id: str,
    service_class: Type[ActuatorService],
    poll_interval: float = 0.5,
    logger: Optional[logging.Logger] = None,
    **service_kwargs: Any,
) -> ActuatorService:
    """
    Connect actuator service to sidecar ENS (simplified setup).

    This factory function hides all the boilerplate:
    - Creates AsyncHarnessClient
    - Sets up SidecarBusAdapter
    - Creates RemoteSeamStore
    - Initializes seam attributes in sidecar
    - Configures PollingBusRouter
    - Returns ready-to-start service

    Args:
        sidecar_url: Sidecar HTTP endpoint (e.g., "http://localhost:8080")
        system_name: System name in sidecar attribute tree
        component_id: Component ID (e.g., "pump01")
        service_class: Your ActuatorService subclass
        poll_interval: Command polling interval in seconds (default: 0.5)
        logger: Optional logger instance
        **service_kwargs: Additional kwargs passed to service_class constructor

    Returns:
        Configured ActuatorService instance, ready to call start()

    Example:
        class MyPump(ActuatorService):
            async def handle_command(self, cmd):
                # Your logic here
                pass

        pump = await connect_actuator(
            "http://localhost:8080",
            "batch_system",
            "pump01",
            MyPump
        )
        await pump.start()  # Service now running
    """
    try:
        from procaaso_client.asynchronous.client import AsyncHarnessClient, AsyncHttpClient
    except ImportError:
        raise ImportError(
            "procaaso_client is required. Install it with: pip install procaaso-client"
        )

    log = logger or logging.getLogger(__name__)

    # Create sidecar client
    http_client = AsyncHttpClient(base_url=sidecar_url)
    sidecar_client = AsyncHarnessClient(http_client=http_client)

    # Create adapter and store
    bus_adapter = SidecarBusAdapter(sidecar_client, system_name, log=log)
    seam_store = RemoteSeamStore(bus_adapter, log=log)

    # Initialize seam attributes in sidecar (prevents 404 errors)
    await _ensure_seam_attributes(seam_store, component_id, log)

    # Create idempotency store (in-memory for now)
    from ..bus.idempotency import IdempotencyStore

    idempotency_store = IdempotencyStore()

    # Create polling router
    router = PollingBusRouter(
        bus=bus_adapter, idempotency_store=idempotency_store, poll_interval=poll_interval, log=log
    )

    # Create service instance
    service = service_class(
        component_id=component_id,
        bus=bus_adapter,  # type: ignore[arg-type]
        store=seam_store,
        router=router,  # type: ignore[arg-type]
        log=log,
        **service_kwargs,
    )

    log.info(f"Connected {service_class.__name__} '{component_id}' to sidecar at {sidecar_url}")
    return service


async def connect_sensor(
    sidecar_url: str,
    system_name: str,
    component_id: str,
    service_class: Type[Any],
    poll_interval: float = 0.5,
    logger: Optional[logging.Logger] = None,
    **service_kwargs: Any,
) -> Any:
    """
    Connect sensor service to sidecar ENS (simplified setup).

    This factory function hides all the boilerplate:
    - Creates AsyncHarnessClient
    - Sets up SidecarBusAdapter
    - Creates RemoteSeamStore
    - Initializes seam attributes in sidecar
    - Configures PollingBusRouter
    - Returns ready-to-start service

    Args:
        sidecar_url: Sidecar HTTP endpoint (e.g., "http://localhost:8080")
        system_name: System name in sidecar attribute tree
        component_id: Component ID (e.g., "temp01")
        service_class: Your SensorService subclass
        poll_interval: Command polling interval in seconds (default: 0.5)
        logger: Optional logger instance
        **service_kwargs: Additional kwargs passed to service_class constructor

    Returns:
        Configured SensorService instance, ready to call start()

    Example:
        class MyTempSensor(SensorService):
            async def handle_command(self, cmd):
                # Your logic here
                pass

        sensor = await connect_sensor(
            "http://localhost:8080",
            "batch_system",
            "temp01",
            MyTempSensor
        )
        await sensor.start()  # Service now running
    """
    try:
        from procaaso_client.asynchronous.client import AsyncHarnessClient, AsyncHttpClient
    except ImportError:
        raise ImportError(
            "procaaso_client is required. Install it with: pip install procaaso-client"
        )

    log = logger or logging.getLogger(__name__)

    # Create sidecar client
    http_client = AsyncHttpClient(base_url=sidecar_url)
    sidecar_client = AsyncHarnessClient(http_client=http_client)

    # Create adapter and store
    bus_adapter = SidecarBusAdapter(sidecar_client, system_name, log=log)
    seam_store = RemoteSeamStore(bus_adapter, log=log)

    # Initialize seam attributes in sidecar (prevents 404 errors)
    await _ensure_sensor_seam_attributes(seam_store, component_id, log)

    # Create idempotency store (in-memory for now)
    from ..bus.idempotency import IdempotencyStore

    idempotency_store = IdempotencyStore()

    # Create polling router
    router = PollingBusRouter(
        bus=bus_adapter, idempotency_store=idempotency_store, poll_interval=poll_interval, log=log
    )

    # Create service instance
    service = service_class(
        component_id=component_id,
        bus=bus_adapter,  # type: ignore[arg-type]
        store=seam_store,
        router=router,  # type: ignore[arg-type]
        log=log,
        **service_kwargs,
    )

    log.info(f"Connected {service_class.__name__} '{component_id}' to sidecar at {sidecar_url}")
    return service


async def _ensure_seam_attributes(store: RemoteSeamStore, component_id: str, log) -> None:
    """
    Initialize all actuator seam attributes in sidecar.

    This prevents 404 errors when first accessing attributes.
    """
    from ..seams.models import (
        ActuatorCapabilities,
        ActuatorCmd,
        ActuatorFeedback,
        ActuatorIntent,
        ActuatorInvariants,
        ActuatorMeta,
        ActuatorState,
    )

    # Define empty/default values for each attribute
    defaults = {
        "meta": ActuatorMeta(
            actuator_id=component_id,
            actuator_type="Actuator",
            contract_version="1.0.0",
        ).dict(),
        "state": ActuatorState(
            lifecycle_state="Idle",
            op_mode="Off",
            comms_ok=True,
            faulted=False,
        ).dict(),
        "capabilities": ActuatorCapabilities(
            supported_modes=["Off"],
            supported_commands=["Noop"],
        ).dict(),
        "feedback": ActuatorFeedback().dict(),
        "intent": ActuatorIntent().dict(),
        "invariants": ActuatorInvariants().dict(),
        "cmd": ActuatorCmd(
            command_id="",
            command="Noop",
        ).dict(),
    }

    # Initialize each attribute
    first_error = None
    for attr_name, default_value in defaults.items():
        try:
            await store.set(component_id, "actuator", attr_name, default_value)
            log.debug(f"Initialized {component_id}.actuator.{attr_name}")
        except Exception as e:
            if first_error is None:
                first_error = e
                log.error(
                    f"Failed to initialize seam attributes. Is the sidecar running? " f"Error: {e}"
                )
            log.debug(f"Failed to initialize {attr_name}: {e}")


async def _ensure_sensor_seam_attributes(store: RemoteSeamStore, component_id: str, log) -> None:
    """
    Initialize all sensor seam attributes in sidecar.

    This prevents 404 errors when first accessing attributes.
    """
    from ..seams.models import (
        SensorCapabilities,
        SensorCmd,
        SensorMeta,
        SensorScaling,
        SensorState,
        SensorValue,
    )

    # Define empty/default values for each attribute
    defaults = {
        "meta": SensorMeta(
            sensor_id=component_id,
            sensor_type="Sensor",
            contract_version="1.0.0",
        ).dict(),
        "state": SensorState(
            lifecycle_state="Offline",
            comms_ok=True,
            faulted=False,
        ).dict(),
        "capabilities": SensorCapabilities(
            supported_commands=["Noop"],
        ).dict(),
        "value": SensorValue().dict(),
        "scaling": SensorScaling().dict(),
        "cmd": SensorCmd(
            command_id="",
            command="Noop",
        ).dict(),
    }

    # Initialize each attribute
    first_error = None
    for attr_name, default_value in defaults.items():
        try:
            await store.set(component_id, "sensor", attr_name, default_value)
            log.debug(f"Initialized {component_id}.sensor.{attr_name}")
        except Exception as e:
            if first_error is None:
                first_error = e
                log.error(
                    f"Failed to initialize seam attributes. Is the sidecar running? " f"Error: {e}"
                )
            log.debug(f"Failed to initialize {attr_name}: {e}")
