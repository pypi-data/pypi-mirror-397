"""Building model construction and simulation orchestration utilities.

.. module:: batem.core.building

This module provides the high-level orchestration logic required to build a
BATEM building model from contextual data, generate thermal networks, configure
HVAC controllers, and run coupled simulations. It binds together solar,
thermal, control, and model-making subsystems to offer a cohesive workflow.

The dataclasses defined here use reStructuredText field lists so that automated
documentation can surface every parameter accepted by the simulation pipeline.

:Author: stephane.ploix@grenoble-inp.fr
:License: GNU General Public License v3.0
"""
from abc import ABC, abstractmethod
from datetime import datetime
from batem.core.data import DataProvider, Bindings
from batem.core.control import HeatingPeriod, CoolingPeriod, OccupancyProfile, SignalGenerator, TemperatureController, Simulation, TemperatureSetpointPort, HVACcontinuousModePort, LongAbsencePeriod
from batem.core.model import ModelMaker
from batem.core.components import Side
from batem.core.library import SIDE_TYPES, SLOPES
from batem.core.solar import SolarModel, SolarSystem, Collector, SideMask, Mask
from batem.core.statemodel import StateModel
from pyvista.core.pointset import PolyData
from dataclasses import dataclass, field
from pyvista.plotting.plotter import Plotter
from math import sqrt, sin, cos, radians, atan2, degrees
import pyvista as pv
import matplotlib.pyplot as plt
import numpy as np
import types
pv.set_jupyter_backend('html')


@dataclass
class WindowData:
    side: str
    surface: float
    rotation_angle_deg: float


@dataclass
class FloorData:
    length: float
    width: float
    elevation: float
    windows_data: list[WindowData]


@dataclass
class SideMaskData:
    x_center: float
    y_center: float
    width: float
    height: float
    elevation: float
    exposure_deg: float
    slope_deg: float
    normal_rotation_angle_deg: float


@dataclass
class ContextData:
    """Metadata describing the geographic and climatic context for a simulation.

    :param latitude_north_deg: Site latitude in decimal degrees (positive north).
    :param longitude_east_deg: Site longitude in decimal degrees (positive east).
    :param starting_stringdate: Inclusive start date for the simulation window.
    :param ending_stringdate: Exclusive end date for the simulation window.
    :param location: Human-readable site name used in reports.
    :param albedo: Ground albedo coefficient in the ``[0, 1]`` range.
    :param pollution: Atmospheric pollution factor used for solar attenuation.
    :param number_of_levels: Number of distinct vertical atmospheric layers to
        load in the weather data set.
    :param ground_temperature: Average ground temperature in degrees Celsius.
    :param side_masks: Optional list of distant masks describing surrounding
        obstacles.
    :ivar side_masks: Always stored as a list for downstream iteration.
    """
    latitude_north_deg: float
    longitude_east_deg: float
    starting_stringdate: str
    ending_stringdate: str
    location: str
    albedo: float
    pollution: float
    number_of_levels: int
    ground_temperature: float
    side_masks: list[SideMaskData] = field(default_factory=list)
    initial_year: int = 1980


@dataclass
class BuildingData:
    """Physical and operational parameters defining a BATEM building model.

    This dataclass stores the geometry, material compositions, HVAC capacities,
    and occupant-related assumptions used when generating thermal networks and
    control systems.

    :param length: Building length along the X-axis in metres.
    :param width: Building width along the Y-axis in metres.
    :param n_floors: Number of occupied floors (excluding the basement zone).
    :param floor_height: Storey height in metres for regular floors.
    :param base_elevation: Basement height in metres.
    :param z_rotation_angle_deg: Clockwise rotation of the building footprint.
    :param ref_glazing_ratio: Ratio of window surface to façade surface for the
        reference side (at rotation_angle_deg, typically South).
    :param right_glazing_ratio: Ratio of window surface to façade surface for the
        right side (at rotation_angle_deg + 90°, typically East).
    :param opposite_glazing_ratio: Ratio of window surface to façade surface for the
        opposite side (at rotation_angle_deg + 180°, typically North).
    :param left_glazing_ratio: Ratio of window surface to façade surface for the
        left side (at rotation_angle_deg - 90°, typically West).
    :param glazing_solar_factor: Solar heat gain coefficient applied to glazing.
    :param shutter_closed_temperature: Outdoor temperature threshold (°C) above which
        shutters are closed and solar gains are set to 0. If None, shutters are never closed.
    :param compositions: Mapping of envelope component names to layer tuples
        ``(material_name, thickness_m)``.
    :param max_heating_power: Maximum heating power available per zone in watts.
    :param max_cooling_power: Maximum cooling power available per zone in watts.
    :param occupant_consumption: Latent/convective gains per occupant in watts.
    :param body_PCO2: CO₂ production per occupant in litres per hour.
    :param density_occupants_per_100m2: Occupant density used for gain profiles.
    :param regular_air_renewal_rate_vol_per_hour: Baseline ventilation rate used
        for nominal operation (volumes per hour).
    :param super_air_renewal_rate_vol_per_hour: Ventilation rate applied during
        forced ventilation or free-cooling strategies (volumes per hour).
    :param initial_temperature: Initial temperature (°C) for all thermal states.
    :param low_heating_setpoint: Setback heating setpoint in degrees Celsius.
    :param normal_heating_setpoint: Comfort heating setpoint in degrees Celsius.
    :param high_heating_setpoint: Boost heating setpoint in degrees Celsius.
    :param state_model_order_max: Optional upper bound for model reduction.
    :param periodic_depth_seconds: Maximum penetration depth for periodic inputs.
    :param combinations: dictionary with keys 'wall', 'intermediate_floor', 'roof', 'glazing', 'ground_floor', 'basement_floor' and values are lists of tuples of materials and thicknesses
    :param intermediate_floor: dict[str, tuple[tuple[str, float], ...]]
    """
    length: float
    width: float
    n_floors: int
    floor_height: float
    base_elevation: float
    z_rotation_angle_deg: float
    ref_glazing_ratio: float
    opposite_glazing_ratio: float
    left_glazing_ratio: float
    right_glazing_ratio: float
    glazing_solar_factor: float
    compositions: dict[str, tuple[tuple[str, float], ...]]
    max_heating_power: float
    max_cooling_power: float
    occupant_consumption: float
    body_PCO2: float
    density_occupants_per_100m2: float
    initial_temperature: float
    low_heating_setpoint: float
    normal_heating_setpoint: float
    normal_cooling_setpoint: float
    regular_air_renewal_rate_vol_per_hour: float
    shutter_closed_temperature: float | None = None  # if not None, shutters are closed and solar gains are set to 0 when outdoor temperature exceeds this threshold
    long_absence_period: tuple[str, str] = ('1/8', '15/8')
    heating_period: tuple[str, str] = ('1/11', '1/5')
    cooling_period: tuple[str, str] = ('1/6', '30/9')
    state_model_order_max: int | None = None
    periodic_depth_seconds: int = 3600
    wall: Side = field(init=False)
    intermediate_floor: Side | None = field(init=False)
    roof: Side = field(init=False)
    glazing: Side = field(init=False)
    ground_floor: Side = field(init=False)
    basement_floor: Side | None = field(init=False)

    def __post_init__(self) -> None:
        """Post initialization method to validate and initialize building components.
        Validates that all required compositions are present and initializes the building components.

        :param self: The instance of the class.
        :raises ValueError: Raised if required compositions are missing.
        """
        # Always required components
        required_components: list[str] = ['wall', 'roof', 'glazing', 'ground_floor']

        # intermediate_floor is only needed when there are multiple floors
        if self.n_floors > 1:
            required_components.append('intermediate_floor')

        # basement_floor is only needed when there's a basement
        if self.base_elevation > 0:
            required_components.append('basement_floor')

        missing_keys: list[str] = [key for key in required_components if key not in self.compositions]
        if missing_keys:
            raise ValueError(f"Missing compositions for: {', '.join(missing_keys)}")

        self.wall = Side(*self.compositions['wall'])
        self.roof = Side(*self.compositions['roof'])
        self.glazing = Side(*self.compositions['glazing'])
        self.ground_floor = Side(*self.compositions['ground_floor'])

        # Initialize optional components only if present
        if 'intermediate_floor' in self.compositions:
            self.intermediate_floor = Side(*self.compositions['intermediate_floor'])
        else:
            self.intermediate_floor = None

        if 'basement_floor' in self.compositions:
            self.basement_floor = Side(*self.compositions['basement_floor'])
        else:
            self.basement_floor = None


class FloorZoneView:

    @staticmethod
    def _normalize(angle: float) -> float:
        return (angle + 180) % 360 - 180

    def __init__(self, xmin: float, xmax: float, ymin: float, ymax: float, zmin: float, zmax: float, ref_glazing_ratio: float = 0.0, right_glazing_ratio: float = 0.0, opposite_glazing_ratio: float = 0.0, left_glazing_ratio: float = 0.0, rotation_angle_deg: float = 0.0) -> None:
        self.xmin: float = xmin
        self.xmax: float = xmax
        self.ymin: float = ymin
        self.ymax: float = ymax
        self.zmin: float = zmin
        self.zmax: float = zmax
        self._rotation_angle_deg: float = rotation_angle_deg
        self.ref_glazing_ratio: float = ref_glazing_ratio
        self.right_glazing_ratio: float = right_glazing_ratio
        self.opposite_glazing_ratio: float = opposite_glazing_ratio
        self.left_glazing_ratio: float = left_glazing_ratio
        # For visualization, use max glazing ratio to determine if windows should be shown
        self.glazing_ratio: float = max(ref_glazing_ratio, right_glazing_ratio, opposite_glazing_ratio, left_glazing_ratio)

        floor_length: float = xmax - xmin
        floor_width: float = ymax - ymin
        floor_height: float = zmax - zmin
        self._elevation: float = (zmin + zmax) / 2
        self._north_south_surface: float = floor_length * floor_height
        self._east_west_surface: float = floor_width * floor_height

    @property
    def floor_center(self) -> tuple:
        return (0, 0, (self.zmin + self.zmax) / 2)

    def make(self) -> pv.PolyData:
        main_box: PolyData = pv.Box(bounds=(self.xmin, self.xmax, self.ymin, self.ymax, self.zmin, self.zmax))
        if self.glazing_ratio == 0:
            return main_box

        floor_length: float = self.xmax - self.xmin
        floor_width: float = self.ymax - self.ymin
        floor_height: float = self.zmax - self.zmin
        elevation: float = (self.zmin + self.zmax) / 2

        self._elevation: float = elevation
        self._north_south_surface: float = floor_length * floor_height
        self._east_west_surface: float = floor_width * floor_height

        # Use a large padding so cutter boxes pass fully through the floor
        pad: float = max(floor_length, floor_width, floor_height) * 5.0
        # Use a small epsilon to position windows slightly inside the building to avoid edge issues
        epsilon: float = 0.01

        # Create window holes for each side with individual glazing ratios
        # Convention: 0°=South(+X), 90°=East(+Y), -90°=West(-Y), 180°=North(-X)
        # ref is at rotation_angle_deg (typically South), opposite is +180°, right is +90°, left is -90°
        # Windows are created as holes that pass through the building
        # To avoid affecting multiple sides, we position windows at the faces and limit their extent
        result: PolyData = main_box

        # Calculate window dimensions for each side based on their individual glazing ratios
        # Window size: width = wall_length * sqrt(glazing_ratio), height = wall_height * sqrt(glazing_ratio)
        # Windows are centered in the middle of each wall
        # ref side (primary direction - typically South, at xmax face)
        # The wall spans in Y direction (floor_width) and Z direction (floor_height)
        # Wall surface = floor_width * floor_height
        # clip_box bounds: (xmin, xmax, ymin, ymax, zmin, zmax)
        if self.ref_glazing_ratio > 0:
            ref_window_width: float = floor_width * sqrt(self.ref_glazing_ratio)
            ref_window_height: float = floor_height * sqrt(self.ref_glazing_ratio)
            ref_window_center_y: float = (self.ymin + self.ymax) / 2  # Centered in middle of wall
            # Position window hole at xmax face - passes through in Y direction
            ref_bounds = (
                self.xmax - epsilon,  # Start just inside xmax face
                self.xmax + pad,  # Extend outward
                ref_window_center_y - ref_window_width/2,
                ref_window_center_y + ref_window_width/2,
                elevation - ref_window_height/2,
                elevation + ref_window_height/2,
            )
            try:
                result = result.clip_box(ref_bounds, invert=True)
            except Exception:
                pass

        # opposite side (primary direction + 180° - typically North, at xmin face)
        # The wall spans in Y direction (floor_width) and Z direction (floor_height)
        # Wall surface = floor_width * floor_height
        if self.opposite_glazing_ratio > 0:
            opposite_window_width: float = floor_width * sqrt(self.opposite_glazing_ratio)
            opposite_window_height: float = floor_height * sqrt(self.opposite_glazing_ratio)
            opposite_window_center_y: float = (self.ymin + self.ymax) / 2  # Centered in middle of wall
            # Position window hole at xmin face - passes through in Y direction
            opposite_bounds = (
                self.xmin - pad,  # Extend outward
                self.xmin + epsilon,  # Start just inside xmin face
                opposite_window_center_y - opposite_window_width/2,
                opposite_window_center_y + opposite_window_width/2,
                elevation - opposite_window_height/2,
                elevation + opposite_window_height/2,
            )
            try:
                result = result.clip_box(opposite_bounds, invert=True)
            except Exception:
                pass

        # right side (secondary direction + 90° - typically East, at ymax face)
        # Note: Windows are created in local coordinates before rotation, so right is at +Y direction
        # The wall spans in X direction (floor_length) and Z direction (floor_height)
        # Wall surface = floor_length * floor_height
        if self.right_glazing_ratio > 0:
            right_window_width: float = floor_length * sqrt(self.right_glazing_ratio)
            right_window_height: float = floor_height * sqrt(self.right_glazing_ratio)
            right_window_center_x: float = (self.xmin + self.xmax) / 2  # Centered in middle of wall
            # Position window hole at ymax face - passes through in X direction
            right_bounds = (
                right_window_center_x - right_window_width/2,
                right_window_center_x + right_window_width/2,
                self.ymax - epsilon,  # Start just inside ymax face
                self.ymax + pad,  # Extend outward
                elevation - right_window_height/2,
                elevation + right_window_height/2,
            )
            try:
                result = result.clip_box(right_bounds, invert=True)
            except Exception:
                pass

        # left side (secondary direction - 90° - typically West, at ymin face)
        # Note: Windows are created in local coordinates before rotation, so left is at -Y direction
        # The wall spans in X direction (floor_length) and Z direction (floor_height)
        # Wall surface = floor_length * floor_height
        if self.left_glazing_ratio > 0:
            left_window_width: float = floor_length * sqrt(self.left_glazing_ratio)
            left_window_height: float = floor_height * sqrt(self.left_glazing_ratio)
            left_window_center_x: float = (self.xmin + self.xmax) / 2  # Centered in middle of wall
            # Position window hole at ymin face - passes through in X direction
            left_bounds = (
                left_window_center_x - left_window_width/2,
                left_window_center_x + left_window_width/2,
                self.ymin - pad,  # Extend outward
                self.ymin + epsilon,  # Start just inside ymin face
                elevation - left_window_height/2,
                elevation + left_window_height/2,
            )
            try:
                result = result.clip_box(left_bounds, invert=True)
            except Exception as e:
                print(f"Clipping operation failed for left window: {e}")

        return result

    @property
    def elevation(self) -> float:
        return self._elevation

    @property
    def windows_data(self) -> list[WindowData]:
        floor_length: float = self.xmax - self.xmin
        floor_width: float = self.ymax - self.ymin
        floor_height: float = self.zmax - self.zmin
        # Calculate window surfaces using individual glazing ratios
        # Order: ref, right, opposite, left
        # Note: ref and opposite walls span in Y direction (floor_width), left and right walls span in X direction (floor_length)
        return [
            WindowData(side="ref", surface=self.ref_glazing_ratio * floor_width * floor_height, rotation_angle_deg=FloorZoneView._normalize(self._rotation_angle_deg)),
            WindowData(side="right", surface=self.right_glazing_ratio * floor_length * floor_height, rotation_angle_deg=FloorZoneView._normalize(self._rotation_angle_deg+90)),
            WindowData(side="opposite", surface=self.opposite_glazing_ratio * floor_width * floor_height, rotation_angle_deg=FloorZoneView._normalize(self._rotation_angle_deg+180)),
            WindowData(side="left", surface=self.left_glazing_ratio * floor_length * floor_height, rotation_angle_deg=FloorZoneView._normalize(self._rotation_angle_deg-90)),
        ]


class BuildingView:

    def __init__(self, length=10.0, width=8.0, n_floors=5, floor_height=2.7, base_elevation=0, ref_glazing_ratio=0.4, right_glazing_ratio=0.4, opposite_glazing_ratio=0.4, left_glazing_ratio=0.4) -> None:
        self._building_data: list[FloorData] = []
        self.rotation_angle_deg: float = None
        self.building_color: str = "lightgray"
        self.base_color: str = "darkgray"
        self.edge_color: str = "black"
        self.length: float = length
        self.width: float = width
        self.n_floors: int = n_floors
        self.floor_height: float = floor_height
        self.base_elevation: float = base_elevation
        self.ref_glazing_ratio: float = ref_glazing_ratio
        self.right_glazing_ratio: float = right_glazing_ratio
        self.opposite_glazing_ratio: float = opposite_glazing_ratio
        self.left_glazing_ratio: float = left_glazing_ratio
        # For backward compatibility in visualization
        self.glazing_ratio: float = max(ref_glazing_ratio, right_glazing_ratio, opposite_glazing_ratio, left_glazing_ratio)
        self.xmin: float = -length/2
        self.xmax: float = length/2
        self.ymin: float = -width/2
        self.ymax: float = width/2
        self.total_height: float = base_elevation + n_floors * floor_height
        self.center_elevation: float = self.total_height / 2
        self.zmin = 0
        self.zmax: float = self.total_height
        self.z_floors: list[float] = [base_elevation + i * floor_height for i in range(n_floors)] + [self.total_height]
        self.floors: list[FloorZoneView] = []
        if base_elevation > 0:
            self.floors.append(FloorZoneView(xmin=self.xmin, xmax=self.xmax, ymin=self.ymin, ymax=self.ymax, zmin=0, zmax=base_elevation, ref_glazing_ratio=0, right_glazing_ratio=0, opposite_glazing_ratio=0, left_glazing_ratio=0))
        self.slabs: list[pv.PolyData] = []
        for i in range(n_floors):
            self.floors.append(FloorZoneView(xmin=self.xmin, xmax=self.xmax, ymin=self.ymin, ymax=self.ymax, zmin=self.z_floors[i], zmax=self.z_floors[i+1], ref_glazing_ratio=ref_glazing_ratio, right_glazing_ratio=right_glazing_ratio, opposite_glazing_ratio=opposite_glazing_ratio, left_glazing_ratio=left_glazing_ratio))
            self.slabs.append(pv.Box(bounds=(self.xmin, self.xmax, self.ymin, self.ymax, self.z_floors[i], self.z_floors[i]+self.total_height/20)))

    def make(self, rotation_angle_deg: float = 0) -> list[FloorData]:
        # rotation_angle_deg follows convention: 0°=South, 90°=East, -90°=West, 180°=North
        self.rotation_angle_deg = rotation_angle_deg
        building_data: list[FloorData] = []
        for floor in self.floors:
            floor._rotation_angle_deg = rotation_angle_deg
            windows_data: list[WindowData] = []
            for window in floor.windows_data:
                windows_data.append(WindowData(side=window.side, surface=window.surface, rotation_angle_deg=window.rotation_angle_deg))
                # floor_data.windows_data.append(window_data)
            floor_data: FloorData = FloorData(length=self.length, width=self.width, elevation=floor.elevation, windows_data=floor.windows_data)
            building_data.append(floor_data)
        self._building_data = building_data
        return self._building_data

    def draw(self, plotter: pv.Plotter) -> None:
        if self.rotation_angle_deg is None:
            self.rotation_angle_deg = 0.0

        base_box: PolyData | None = None
        if self.floors and self.base_elevation > 0:
            base_box = self.floors[0].make().rotate_z(self.rotation_angle_deg, inplace=False)
        # Upper floors have windows
        upper_boxes: list[PolyData] = []
        start_index = 1 if self.base_elevation > 0 else 0
        for floor in self.floors[start_index:]:
            floor._rotation_angle_deg = self.rotation_angle_deg
            upper_boxes.append(floor.make().rotate_z(self.rotation_angle_deg, inplace=False))

        merged_upper: PolyData | None = None
        if upper_boxes:
            merged_upper = upper_boxes[0].copy()
            for ub in upper_boxes[1:]:
                merged_upper = merged_upper.merge(ub)

        # Slabs
        slab_boxes: list[PolyData] = [slab.rotate_z(self.rotation_angle_deg, inplace=False) for slab in self.slabs]

        for slab in slab_boxes:  # type: ignore[index]
            plotter.add_mesh(slab, color=self.building_color, opacity=0.2, show_edges=False)
        if base_box is not None:
            plotter.add_mesh(base_box, color=self.base_color, smooth_shading=True, metallic=0.1, roughness=0.6, show_edges=True, edge_color="black", line_width=1.5)  # type: ignore[arg-type]
        if merged_upper is not None:
            plotter.add_mesh(merged_upper, color=self.building_color, smooth_shading=True, metallic=0.1, roughness=0.6, show_edges=True, edge_color=self.edge_color, line_width=1.5)  # type: ignore[arg-type]

        building_data: list[FloorData] = []
        for floor in self.floors:
            windows_data: list[WindowData] = []
            for window in floor.windows_data:
                windows_data.append(WindowData(side=window.side, surface=window.surface, rotation_angle_deg=window.rotation_angle_deg))
            floor_data: FloorData = FloorData(length=self.length, width=self.width, elevation=floor.elevation, windows_data=floor.windows_data)
            building_data.append(floor_data)
        self._building_data = building_data

    @property
    def building_data(self) -> list[FloorData]:
        return self._building_data


class SideMaskView:

    def __init__(self, side_mask_data: SideMaskData) -> None:
        self.color: str = "red"
        self.opacity: float = 0.35
        # World coordinates: +X=South, +Y=East (as requested)
        self.x_center: float = side_mask_data.x_center
        self.y_center: float = side_mask_data.y_center
        self.z_center: float = side_mask_data.elevation + side_mask_data.height / 2
        self.center_ref: tuple[float, float, float] = (side_mask_data.x_center, side_mask_data.y_center, self.z_center)
        self.width: float = side_mask_data.width
        self.height: float = side_mask_data.height
        self.elevation: float = side_mask_data.elevation
        self.exposure_deg: float = side_mask_data.exposure_deg
        self.slope_deg: float = side_mask_data.slope_deg
        self.normal_rotation_deg: float = side_mask_data.normal_rotation_angle_deg

        self.azimuth_deg: float = degrees(atan2(self.y_center, self.x_center))
        self.altitude_deg: float = degrees(atan2(self.elevation, sqrt(self.x_center**2 + self.y_center**2)))
        self.distance_m: float = sqrt(self.x_center**2 + self.y_center**2)

        slope_rad: float = radians(self.slope_deg)
        # Convention: +X is South, +Y is East; 0°=South(+X), 90°=East(+Y), -90°=West(-Y), 180°=North(-X)
        exposure_rad: float = radians(side_mask_data.exposure_deg)

        # Normal mapping in world XY directly: (cos(theta), sin(theta))
        nx: float = cos(exposure_rad) * sin(slope_rad)
        ny: float = sin(exposure_rad) * sin(slope_rad)
        nz: float = -cos(slope_rad)
        self.normal: tuple[float, float, float] = (nx, ny, nz)

    def make(self) -> SideMaskData:
        return SideMaskData(x_center=self.x_center, y_center=self.y_center, width=self.width, height=self.height, elevation=self.elevation, exposure_deg=self.exposure_deg, slope_deg=self.slope_deg, normal_rotation_angle_deg=self.normal_rotation_deg)

    def draw(self, plotter: pv.Plotter) -> None:
        plane: pv.Plane = pv.Plane(center=self.center_ref, direction=self.normal, i_size=self.height, j_size=self.width)
        if abs(self.normal_rotation_deg) > 1e-9:
            plane.rotate_vector(vector=self.normal, angle=self.normal_rotation_deg, point=self.center_ref, inplace=True)
        tail: list[float] = self.center_ref
        head: list[float] = (self.center_ref[0] + 3.0 * self.normal[0], self.center_ref[1] + 3.0 * self.normal[1], self.center_ref[2] + 3.0 * self.normal[2])
        arrow: pv.Arrow = pv.Arrow(start=tail, direction=[head[i] - tail[i] for i in range(3)], tip_length=0.2, tip_radius=0.15, shaft_radius=0.05)

        plotter.add_mesh(plane, color=self.color, opacity=self.opacity, smooth_shading=True)
        plotter.add_mesh(arrow, color="black")


class Context:

    def __init__(self, context_data: ContextData) -> None:
        self.context_data: ContextData = context_data
        self.distant_masks: list[SideMask] = list()
        self.side_mask_views: list[SideMaskView] = list()
        for side_mask in context_data.side_masks:
            self.distant_masks.append(SideMask(side_mask.x_center, side_mask.y_center, side_mask.width, side_mask.height, side_mask.exposure_deg, side_mask.slope_deg, side_mask.elevation, side_mask.normal_rotation_angle_deg))
            side_mask_view: SideMaskView = SideMaskView(side_mask)
            side_mask_view.make()
            self.side_mask_views.append(side_mask_view)

        bindings: Bindings = Bindings()
        bindings('TZ:outdoor', 'weather_temperature')

        self.dp: DataProvider = DataProvider(location=context_data.location, latitude_north_deg=context_data.latitude_north_deg, longitude_east_deg=context_data.longitude_east_deg, starting_stringdate=context_data.starting_stringdate, ending_stringdate=context_data.ending_stringdate, bindings=bindings, albedo=context_data.albedo, pollution=context_data.pollution, number_of_levels=context_data.number_of_levels, initial_year=context_data.initial_year)
        self.solar_model: SolarModel = SolarModel(self.dp.weather_data, distant_masks=self.distant_masks)


class Zone(ABC):

    def __init__(self, floor_number: int, building_data: BuildingData, solar_model: SolarModel) -> None:
        self.floor_number: int = floor_number
        self.name: str = f"floor{floor_number}"
        self.length: float = building_data.length
        self.width: float = building_data.width
        self.floor_height: float = building_data.floor_height
        self.floor_surface: float = self.length * self.width
        self.base_elevation: float = building_data.base_elevation
        self.z_rotation_angle_deg: float = building_data.z_rotation_angle_deg
        self.building_data: BuildingData = building_data
        self.solar_model: SolarModel = solar_model
        self.solar_system: SolarSystem = SolarSystem(solar_model)
        self.n_floors: int = building_data.n_floors

    @abstractmethod
    def make(self, model_maker: ModelMaker, dp: DataProvider) -> None:
        pass

    @abstractmethod
    def window_masks(self) -> dict[str, Mask]:
        """Return window masks dictionary."""
        pass


class BasementZone(Zone):

    def __init__(self, floor_number: int, building_data: BuildingData, solar_model: SolarModel) -> None:
        super().__init__(floor_number, building_data, solar_model)
        self.volume: float = self.length * self.width * self.base_elevation
        self.mid_elevation: float = self.building_data.base_elevation/2
        self.wall_surface: float = 2 * (self.length + self.width) * self.base_elevation

    def window_masks(self) -> dict[str, Mask]:
        return dict()

    def make(self, model_maker: ModelMaker, dp: DataProvider) -> None:
        # basement_floor is guaranteed to exist when BasementZone is created (base_elevation > 0)
        assert self.building_data.basement_floor is not None, "basement_floor should be defined when base_elevation > 0"
        model_maker.make_side(self.building_data.basement_floor(self.name, 'ground', SIDE_TYPES.FLOOR, self.floor_surface))
        model_maker.make_side(self.building_data.wall(self.name, 'outdoor', SIDE_TYPES.WALL, self.wall_surface))
        model_maker.make_side(self.building_data.ground_floor(self.name, 'floor1', SIDE_TYPES.FLOOR, self.floor_surface))


class RegularZone(Zone):

    def __init__(self, floor_number: int, building_data: BuildingData, solar_model: SolarModel) -> None:
        super().__init__(floor_number, building_data, solar_model)
        self.volume: float = self.length * self.width * self.floor_height
        self.mid_elevation: float = self.base_elevation + self.floor_height * (floor_number - 1 / 2)
        self.window_angles_deg: list[float] = [self.z_rotation_angle_deg, 90+self.z_rotation_angle_deg, 180+self.z_rotation_angle_deg, -90+self.z_rotation_angle_deg]
        # Calculate window surfaces using individual glazing ratios for each side
        # Order: ref, right, opposite, left
        # Note: ref and opposite walls span in Y direction (width), left and right walls span in X direction (length)
        self.window_surfaces: list[float] = [
            building_data.ref_glazing_ratio * self.width * self.floor_height,  # ref (primary direction)
            building_data.right_glazing_ratio * self.length * self.floor_height,  # right (secondary direction)
            building_data.opposite_glazing_ratio * self.width * self.floor_height,  # opposite (primary direction)
            building_data.left_glazing_ratio * self.length * self.floor_height  # left (secondary direction)
        ]
        # Total glazing surface for thermal model
        self.glazing_surface: float = sum(self.window_surfaces)
        self.wall_surface: float = 2 * (self.length + self.width) * self.floor_height - self.glazing_surface
        self._window_masks: dict[str, Mask] = dict()
        self.zone_window_collectors: list[Collector] = []
        self.windows_names: list[str] = ['ref', 'right', 'opposite', 'left']

    def window_masks(self) -> dict[str, Mask]:
        return self._window_masks

    def make(self, model_maker: ModelMaker, dp: DataProvider) -> None:
        # n_floors is the number of regular floors, so the top floor number equals n_floors
        if self.floor_number == self.n_floors:
            model_maker.make_side(self.building_data.roof(self.name, 'outdoor', SIDE_TYPES.CEILING, self.volume))
        else:
            # intermediate_floor is guaranteed to exist when there are multiple floors (n_floors > 1)
            assert self.building_data.intermediate_floor is not None, "intermediate_floor should be defined when n_floors > 1"
            model_maker.make_side(self.building_data.intermediate_floor(self.name, f'floor{self.floor_number+1}', SIDE_TYPES.FLOOR, self.floor_surface))
        # If this is the first floor (floor_number == 1) and there's no basement (base_elevation == 0), connect to ground
        if self.floor_number == 1 and self.base_elevation == 0:
            model_maker.make_side(self.building_data.ground_floor(self.name, 'ground', SIDE_TYPES.FLOOR, self.floor_surface))
        model_maker.make_side(self.building_data.wall(self.name, 'outdoor', SIDE_TYPES.WALL, self.wall_surface))
        model_maker.make_side(self.building_data.glazing(self.name, 'outdoor', SIDE_TYPES.GLAZING, self.glazing_surface))
        regular_rate = self.building_data.regular_air_renewal_rate_vol_per_hour
        if regular_rate is not None:
            nominal_airflow = regular_rate * self.volume / 3600
        else:
            nominal_airflow = 0.0
        model_maker.connect_airflow(self.name, 'outdoor', nominal_value=nominal_airflow)

        for window_name, window_angle, window_surface in zip(self.windows_names, self.window_angles_deg, self.window_surfaces):
            window_collector: Collector = Collector(self.solar_system, f'{window_name}', surface_m2=window_surface, exposure_deg=window_angle, slope_deg=SLOPES.VERTICAL.value, solar_factor=self.building_data.glazing_solar_factor, observer_elevation_m=self.mid_elevation)
            self.zone_window_collectors.append(window_collector)
            self._window_masks[window_name] = window_collector.mask


class Building:
    """High-level orchestrator for generating and simulating a BATEM building.

    The class assembles the context, solar model, thermal network, HVAC
    controllers, and simulation engine required to execute a full-year building
    simulation.

    :param context_data: Geographic and climatic context description.
    :param building_data: Physical parameters and HVAC capacities.
    :ivar context: Instantiated :class:`Context` wrapping weather and bindings.
    :ivar dp: Shared :class:`~batem.core.data.DataProvider` used across modules.
    :ivar simulation: Configured :class:`~batem.core.control.Simulation` object.
    :ivar floors: List of :class:`Zone` instances representing each building
        level.
    """

    def __init__(self, context_data: ContextData, building_data: BuildingData) -> None:
        self.context: Context = Context(context_data)
        self.context_data: ContextData = context_data
        self.dp: DataProvider = self.context.dp
        self.building_data: BuildingData = building_data
        self.building_view: BuildingView = BuildingView(length=building_data.length, width=building_data.width, n_floors=building_data.n_floors, floor_height=building_data.floor_height, base_elevation=building_data.base_elevation, ref_glazing_ratio=building_data.ref_glazing_ratio, right_glazing_ratio=building_data.right_glazing_ratio, opposite_glazing_ratio=building_data.opposite_glazing_ratio, left_glazing_ratio=building_data.left_glazing_ratio)
        self.building_view.make(rotation_angle_deg=building_data.z_rotation_angle_deg)
        self.dp.add_param('CCO2:outdoor', 400)
        self.dp.add_param('TZ:ground', context_data.ground_temperature)

        solar_model: SolarModel = self.context.solar_model

        floors: list[Zone] = []
        zone_name_volumes: dict[str, float] = {}
        if building_data.base_elevation > 0:
            floors.append(BasementZone(0, building_data, solar_model))
            zone_name_volumes[floors[0].name] = floors[0].volume
        # n_floors represents the number of regular floors (excluding basement)
        # So we create floors 1 through n_floors
        for floor_number in range(1, building_data.n_floors + 1):
            floor = RegularZone(floor_number, building_data, solar_model)
            floors.append(floor)
            zone_name_volumes[floor.name] = floor.volume
        zone_name_volumes['outdoor'] = None
        zone_name_volumes['ground'] = None
        self.zone_names: list[str] = [floor.name for floor in floors]
        self.floors: list[Zone] = floors
        self.zone_outdoor_regular_airflows_m3_per_s: dict[str, float] = {}
        airflow_defaults: dict[str, float] = {}
        airflow_bounds: dict[str, float] = {}
        airflow_names: list[str] = []
        for floor in floors:
            volume: float | None = getattr(floor, 'volume', None)
            if volume is None:
                continue
            airflow_name = f'Q:{floor.name}-outdoor'
            base_value: float | None = None
            bound_upper: float = 0.0
            if self.building_data.regular_air_renewal_rate_vol_per_hour is not None:
                print(f"Floor {floor.name} has a regular airflow: {self.building_data.regular_air_renewal_rate_vol_per_hour} vol/h")
                regular_airflow_m3_per_s: float = (self.building_data.regular_air_renewal_rate_vol_per_hour * volume) / 3600.0
                self.zone_outdoor_regular_airflows_m3_per_s[floor.name] = regular_airflow_m3_per_s
                base_value = regular_airflow_m3_per_s
                bound_upper = max(bound_upper, regular_airflow_m3_per_s)
            if base_value is None:
                base_value = 0.0
            bound_upper = max(bound_upper, base_value)
            airflow_defaults[airflow_name] = base_value
            airflow_bounds[airflow_name] = bound_upper
            airflow_names.append(airflow_name)
        if airflow_names:
            self.dp.add_data_names_in_fingerprint(*airflow_names)
            for airflow_name, default_value in airflow_defaults.items():
                values = [default_value for _ in self.dp.ks]
                if airflow_name in self.dp:
                    self.dp.add_var(airflow_name, values, force=True)
                else:
                    self.dp.add_var(airflow_name, values)
                bound_upper = airflow_bounds.get(airflow_name, default_value)
                if bound_upper <= 0.0:
                    bound_upper = 1e-6
                if hasattr(self.dp, 'independent_variable_set'):
                    self.dp.independent_variable_set.variable_bounds[airflow_name] = (0.0, bound_upper)

        # #### STATE MODEL MAKER AND SURFACES ####
        model_maker: ModelMaker = ModelMaker(data_provider=self.dp, periodic_depth_seconds=building_data.periodic_depth_seconds, state_model_order_max=building_data.state_model_order_max, **zone_name_volumes)

        max_occupancy: float = building_data.density_occupants_per_100m2 * (building_data.length * building_data.width) / 100

        siggen: SignalGenerator = SignalGenerator(self.dp, OccupancyProfile(weekday_profile={0: max_occupancy, 7: max_occupancy*.95, 8: max_occupancy*.7, 9: max_occupancy*.3, 12: max_occupancy*.5, 17: max_occupancy*.7, 18: max_occupancy*.8, 19: max_occupancy*.9, 20: max_occupancy}, weekend_profile={0: max_occupancy}))
        siggen.add_hvac_period(HeatingPeriod(building_data.heating_period[0], building_data.heating_period[1], weekday_profile={0: building_data.low_heating_setpoint, 7: building_data.normal_heating_setpoint}, weekend_profile={00: building_data.low_heating_setpoint, 7: building_data.normal_heating_setpoint}))
        siggen.add_hvac_period(CoolingPeriod(building_data.cooling_period[0], building_data.cooling_period[1], weekday_profile={0: None, 10: building_data.normal_cooling_setpoint, 18: None}, weekend_profile={0: None, 10: building_data.normal_cooling_setpoint, 18: None}))
        if building_data.long_absence_period is not None:
            siggen.add_long_absence_period(LongAbsencePeriod(building_data.long_absence_period[0], building_data.long_absence_period[1]))
        else:
            siggen.add_long_absence_period(LongAbsencePeriod(building_data.long_absence_period[0], building_data.long_absence_period[1]))
        # Create per-floor signals
        controllers: dict[str, TemperatureController] = {}

        for floor in floors:
            floor.make(model_maker, self.dp)
            # Occupancy profile and HVAC seasons
            if floor.floor_number == 0:
                # Basement: generate signals but no HVAC controller
                siggen.generate(floor.name)
            else:
                # Regular floors: generate signals (SETPOINT, MODE, OCCUPANCY, PRESENCE)
                siggen.generate(floor.name)
                # Get solar gain (returns None if no collectors)
                solar_gain = floor.solar_system.powers_W(gather_collectors=True)
                # Handle case where there are no collectors (solar_gain is None)
                if solar_gain is None:
                    solar_gain = [0.0 for _ in self.dp.ks]
                # Apply shutter control: set solar gains to 0 when outdoor temperature exceeds threshold
                if building_data.shutter_closed_temperature is not None:
                    weather_temperature = self.dp.series('weather_temperature')
                    solar_gain = [0.0 if weather_temperature[k] > building_data.shutter_closed_temperature else solar_gain[k] for k in self.dp.ks]
                self.dp.add_var(f'GAIN_SOLAR:{floor.name}', solar_gain)
                # Add solar to gains
                zone_occupancy: list[float | None] = self.dp.series(f'OCCUPANCY:{floor.name}')

                # Handle None values in occupancy (convert None to 0 for gain calculation)
                # OCCUPANCY contains the actual number of occupants (0 to max_occupancy), not a ratio
                occupancy_gain: list[float] = [(building_data.occupant_consumption) * (_ if _ is not None else 0.0) for _ in zone_occupancy]
                self.dp.add_var(f'GAIN_OCCUPANCY:{floor.name}', occupancy_gain)
                self.dp.add_var(f'GAIN:{floor.name}', [occupancy_gain[k] + solar_gain[k] for k in self.dp.ks])
                self.dp.add_var(f'PCO2:{floor.name}', (siggen.filter(zone_occupancy, lambda x: x * building_data.body_PCO2 if x is not None else 0)))

        model_maker.zones_to_simulate({floor.name: floor.volume for floor in floors})
        # Nominal state model - must be created before TemperatureControllers
        model_maker.nominal
        if self.building_data.initial_temperature is not None:
            self._initialize_state_models(model_maker, self.building_data.initial_temperature)

        # Create HVAC controllers after nominal state model is ready
        for floor in floors:
            if floor.floor_number > 0:
                hvac_port: HVACcontinuousModePort = HVACcontinuousModePort(data_provider=self.dp, zone_name=floor.name, max_heating_power=building_data.max_heating_power, max_cooling_power=building_data.max_cooling_power)
                temperature_setpoint_port: TemperatureSetpointPort = TemperatureSetpointPort(data_provider=self.dp, zone_name=floor.name, heating_levels=[16, 19, 20, 21, 22, 23, 24], cooling_levels=[24, 25, 26, 27, 28])
                controllers[floor.name] = TemperatureController(hvac_heat_port=hvac_port, temperature_setpoint_port=temperature_setpoint_port, model_maker=model_maker)

        self.simulation: Simulation = Simulation(model_maker)
        for floor in floors:
            if floor.floor_number > 0:
                self.simulation.add_temperature_controller(zone_name=floor.name, temperature_controller=controllers[floor.name])

    def _initialize_state_models(self, model_maker: ModelMaker, temperature: float) -> None:
        def _set_uniform_initial_state(state_model: StateModel, temp: float) -> StateModel:
            if state_model is None or state_model.n_states == 0:
                return state_model
            target_state: np.ndarray = np.full((state_model.n_states, 1), float(temp))
            state_model.set_state(target_state)
            return state_model

        if hasattr(model_maker, "state_models_cache"):
            model_maker.state_models_cache = {
                key: _set_uniform_initial_state(sm, temperature) for key, sm in model_maker.state_models_cache.items()
            }

        nominal_model: StateModel | None = getattr(model_maker, "nominal_state_model", None)
        if nominal_model is not None:
            _set_uniform_initial_state(nominal_model, temperature)

        original_make_k = model_maker.make_k

        def make_k_with_initial_state(self, *args, **kwargs):
            state_model: StateModel = original_make_k(*args, **kwargs)
            return _set_uniform_initial_state(state_model, temperature)

        model_maker.make_k = types.MethodType(make_k_with_initial_state, model_maker)

    def simulate(self, suffix: str = 'sim') -> DataProvider:
        # #### RUN ####
        self.simulation.run(suffix=suffix)

        # #### PRINT/SHOW RESULTS ####
        print(self.simulation)
        print(self.simulation.control_ports)
        return self.dp

    def draw(self, window_size: tuple[int, int] = (1024, 768)) -> None:
        plotter: Plotter = pv.Plotter(window_size=window_size)
        plotter.set_background("white")
        plotter.clear()
        if self.building_view is not None:
            self.building_view.draw(plotter)
        ground: PolyData = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=60, j_size=60)
        plotter.add_mesh(ground, color="#DDDDDD", opacity=1)
        if self.context.side_mask_views is not None:
            for side_mask_view in self.context.side_mask_views:
                side_mask_view.draw(plotter)
        plotter.add_axes(line_width=2)
        plotter.show_bounds(grid="front", location="outer", all_edges=True, xtitle="X (North -> South)", ytitle="Y (West -> East)", ztitle="Z (Up)")
        plotter.enable_eye_dome_lighting()
        plotter.camera_position = [(25, -35, 25), (0, 0, 5), (0, 0, 1)]
        plotter.show(auto_close=False)

    def plot_heliodon(self, floor_number: int) -> plt.Axes:
        """Plot heliodon charts with horizon mask and collector-specific side masks for each floor.

        Generates one heliodon chart per floor showing the complete mask (horizon + distant + collector)
        for the South-facing window, demonstrating how solar access changes with floor elevation.

        :param floor_number: Floor number to plot (1-based index)
        :type floor_number: int (from 0 ground floor to n_floors - 1 to top floor)
        :param year: Year for heliodon plot (defaults to first year in weather data)
        :type collector_name: str (name of the collector to plot)
        :type collector_name: str (name of the collector to plot)
        :type year: int, optional
        """
        # Get year from weather data if not provided

        first_date: datetime = self.dp.weather_data.datetimes[0]
        year: int = first_date.year
        # Find the floor by matching floor_number attribute (not by index, since indices depend on whether basement exists)
        floor: Zone | None = None
        for f in self.floors:
            if f.floor_number == floor_number:
                floor = f
                break
        if floor is None:
            raise ValueError(f'Floor number {floor_number} not found in building')
        window_masks_dict: dict[str, Mask] = floor.window_masks()
        if len(window_masks_dict) == 0:
            # Skip floors with no windows (e.g., basement)
            return None
        
        # Filter windows to only include those with surface > 0
        # Check if floor has window_surfaces attribute (RegularZone) and filter accordingly
        windows_with_surface: dict[str, Mask] = {}
        if hasattr(floor, 'window_surfaces') and hasattr(floor, 'windows_names'):
            for window_name, window_surface in zip(floor.windows_names, floor.window_surfaces):
                if window_name in window_masks_dict and window_surface > 0:
                    windows_with_surface[window_name] = window_masks_dict[window_name]
        else:
            # Fallback: use all windows if we can't check surface
            windows_with_surface = window_masks_dict
        
        if len(windows_with_surface) == 0:
            # Skip floors with no windows with surface > 0
            return None
        
        # Calculate grid size based on number of windows
        n_windows = len(windows_with_surface)
        if n_windows == 1:
            n_rows, n_cols = 1, 1
        elif n_windows == 2:
            n_rows, n_cols = 1, 2
        elif n_windows == 3:
            n_rows, n_cols = 2, 2
        else:  # 4 or more
            n_rows, n_cols = 2, 2
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 8))
        if n_windows == 1:
            axes = [axes]  # Make it a list for consistent iteration
        else:
            axes = axes.flatten()  # Flatten 2D array to 1D for easier indexing
        fig.suptitle(f'Heliodon for {floor.name}, Elevation: {floor.mid_elevation:.1f}m', fontsize=12)
        
        for i, (window_name, window_mask) in enumerate(windows_with_surface.items()):
            if i >= len(axes):
                break  # Safety check: don't exceed available subplots
            self.context.solar_model.plot_heliodon(name=f'Window {window_name}', year=year, observer_elevation_m=floor.mid_elevation, mask=window_mask, axes=axes[i])
            axes[i].set_title(f'Window {window_name}')
            axes[i].set_xlabel('Azimuth in degrees (0° = South, +90° =West)')
        
        # Hide unused subplots
        for i in range(len(windows_with_surface), len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        return axes
