"""Dataclasses for the used vehicle parameters."""

from dataclasses import dataclass
from dataclasses import field


@dataclass
class MFSimpleParams:
    """Dataclass for storing MF Simple parameters."""

    B: float = 0
    C: float = 0
    D: float = 0
    E: float = 0
    S_V: float = 0
    S_H: float = 0


@dataclass
class MFCombinedParams:
    """Dataclass for storing MF Combined parameters."""

    kappa_lon: float = 0
    kappa_lat: float = 0
    mf_params: MFSimpleParams = field(default_factory=lambda: MFSimpleParams(0, 0, 0, 0, 0, 0))


@dataclass
class STMTireParams:
    """Dataclass for storing STM Tire parameters."""

    front_axle_x: MFSimpleParams = field(default_factory=lambda: MFSimpleParams(0, 0, 0, 0, 0, 0))
    front_axle_y: MFSimpleParams = field(default_factory=lambda: MFSimpleParams(0, 0, 0, 0, 0, 0))
    rear_axle_x: MFSimpleParams = field(default_factory=lambda: MFSimpleParams(0, 0, 0, 0, 0, 0))
    rear_axle_y: MFSimpleParams = field(default_factory=lambda: MFSimpleParams(0, 0, 0, 0, 0, 0))
