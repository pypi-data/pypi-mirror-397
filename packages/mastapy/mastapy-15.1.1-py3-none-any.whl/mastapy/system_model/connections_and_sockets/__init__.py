"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.system_model.connections_and_sockets._2524 import (
        AbstractShaftToMountableComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2525 import (
        BearingInnerSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2526 import (
        BearingOuterSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2527 import (
        BeltConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2528 import (
        CoaxialConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2529 import (
        ComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2530 import (
        ComponentMeasurer,
    )
    from mastapy._private.system_model.connections_and_sockets._2531 import Connection
    from mastapy._private.system_model.connections_and_sockets._2532 import (
        CVTBeltConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2533 import (
        CVTPulleySocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2534 import (
        CylindricalComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2535 import (
        CylindricalSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2536 import (
        DatumMeasurement,
    )
    from mastapy._private.system_model.connections_and_sockets._2537 import (
        ElectricMachineStatorSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2538 import (
        InnerShaftSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2539 import (
        InnerShaftSocketBase,
    )
    from mastapy._private.system_model.connections_and_sockets._2540 import (
        InterMountableComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2541 import (
        MountableComponentInnerSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2542 import (
        MountableComponentOuterSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2543 import (
        MountableComponentSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2544 import (
        OuterShaftSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2545 import (
        OuterShaftSocketBase,
    )
    from mastapy._private.system_model.connections_and_sockets._2546 import (
        PlanetaryConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2547 import (
        PlanetarySocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2548 import (
        PlanetarySocketBase,
    )
    from mastapy._private.system_model.connections_and_sockets._2549 import PulleySocket
    from mastapy._private.system_model.connections_and_sockets._2550 import (
        RealignmentResult,
    )
    from mastapy._private.system_model.connections_and_sockets._2551 import (
        RollingRingConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2552 import (
        RollingRingSocket,
    )
    from mastapy._private.system_model.connections_and_sockets._2553 import ShaftSocket
    from mastapy._private.system_model.connections_and_sockets._2554 import (
        ShaftToMountableComponentConnection,
    )
    from mastapy._private.system_model.connections_and_sockets._2555 import Socket
    from mastapy._private.system_model.connections_and_sockets._2556 import (
        SocketConnectionOptions,
    )
    from mastapy._private.system_model.connections_and_sockets._2557 import (
        SocketConnectionSelection,
    )
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.system_model.connections_and_sockets._2524": [
            "AbstractShaftToMountableComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2525": ["BearingInnerSocket"],
        "_private.system_model.connections_and_sockets._2526": ["BearingOuterSocket"],
        "_private.system_model.connections_and_sockets._2527": ["BeltConnection"],
        "_private.system_model.connections_and_sockets._2528": ["CoaxialConnection"],
        "_private.system_model.connections_and_sockets._2529": ["ComponentConnection"],
        "_private.system_model.connections_and_sockets._2530": ["ComponentMeasurer"],
        "_private.system_model.connections_and_sockets._2531": ["Connection"],
        "_private.system_model.connections_and_sockets._2532": ["CVTBeltConnection"],
        "_private.system_model.connections_and_sockets._2533": ["CVTPulleySocket"],
        "_private.system_model.connections_and_sockets._2534": [
            "CylindricalComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2535": ["CylindricalSocket"],
        "_private.system_model.connections_and_sockets._2536": ["DatumMeasurement"],
        "_private.system_model.connections_and_sockets._2537": [
            "ElectricMachineStatorSocket"
        ],
        "_private.system_model.connections_and_sockets._2538": ["InnerShaftSocket"],
        "_private.system_model.connections_and_sockets._2539": ["InnerShaftSocketBase"],
        "_private.system_model.connections_and_sockets._2540": [
            "InterMountableComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2541": [
            "MountableComponentInnerSocket"
        ],
        "_private.system_model.connections_and_sockets._2542": [
            "MountableComponentOuterSocket"
        ],
        "_private.system_model.connections_and_sockets._2543": [
            "MountableComponentSocket"
        ],
        "_private.system_model.connections_and_sockets._2544": ["OuterShaftSocket"],
        "_private.system_model.connections_and_sockets._2545": ["OuterShaftSocketBase"],
        "_private.system_model.connections_and_sockets._2546": ["PlanetaryConnection"],
        "_private.system_model.connections_and_sockets._2547": ["PlanetarySocket"],
        "_private.system_model.connections_and_sockets._2548": ["PlanetarySocketBase"],
        "_private.system_model.connections_and_sockets._2549": ["PulleySocket"],
        "_private.system_model.connections_and_sockets._2550": ["RealignmentResult"],
        "_private.system_model.connections_and_sockets._2551": [
            "RollingRingConnection"
        ],
        "_private.system_model.connections_and_sockets._2552": ["RollingRingSocket"],
        "_private.system_model.connections_and_sockets._2553": ["ShaftSocket"],
        "_private.system_model.connections_and_sockets._2554": [
            "ShaftToMountableComponentConnection"
        ],
        "_private.system_model.connections_and_sockets._2555": ["Socket"],
        "_private.system_model.connections_and_sockets._2556": [
            "SocketConnectionOptions"
        ],
        "_private.system_model.connections_and_sockets._2557": [
            "SocketConnectionSelection"
        ],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "AbstractShaftToMountableComponentConnection",
    "BearingInnerSocket",
    "BearingOuterSocket",
    "BeltConnection",
    "CoaxialConnection",
    "ComponentConnection",
    "ComponentMeasurer",
    "Connection",
    "CVTBeltConnection",
    "CVTPulleySocket",
    "CylindricalComponentConnection",
    "CylindricalSocket",
    "DatumMeasurement",
    "ElectricMachineStatorSocket",
    "InnerShaftSocket",
    "InnerShaftSocketBase",
    "InterMountableComponentConnection",
    "MountableComponentInnerSocket",
    "MountableComponentOuterSocket",
    "MountableComponentSocket",
    "OuterShaftSocket",
    "OuterShaftSocketBase",
    "PlanetaryConnection",
    "PlanetarySocket",
    "PlanetarySocketBase",
    "PulleySocket",
    "RealignmentResult",
    "RollingRingConnection",
    "RollingRingSocket",
    "ShaftSocket",
    "ShaftToMountableComponentConnection",
    "Socket",
    "SocketConnectionOptions",
    "SocketConnectionSelection",
)
