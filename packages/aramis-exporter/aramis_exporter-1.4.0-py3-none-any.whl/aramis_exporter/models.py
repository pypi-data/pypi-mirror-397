"""Models for Aramis Exporter and GOM Client."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, List

import numpy as np


@dataclass
class ValueElement:
    name: str
    type: str
    value: Any


@dataclass
class SignalData:
    inspection_value_elements: Optional[List[ValueElement]] = None
    value_elements: Optional[List[ValueElement]] = None
    analog_inputs: Optional[List[ValueElement]] = None


@dataclass
class StageObjMetadata:
    index: int
    id: int
    name: str
    date: datetime
    nanoseconds: int
    rel_time: float


@dataclass
class ProcessMetadata:
    application_name: str
    application_version: str
    application_revision: str
    application_build_date: str
    current_user: str
    gom_project_file: str
    project_creation_time: str
    aramis_data_exporter_version: str


@dataclass
class CalibrationMetadata:
    camera_angle: Optional[float] = None
    camera_focal_length: Optional[float] = None
    calibration_date: Optional[str] = None
    calibration_deviation: Optional[float] = None
    deviation_optimized: Optional[float] = None
    height_variance: Optional[float] = None
    is_overexposure_check_ignored: Optional[bool] = None
    is_quick_calibrated: Optional[bool] = None
    laser_calibration_deviation: Optional[float] = None
    light_intensity: Optional[float] = None
    limit_value_calibration_deviation: Optional[float] = None
    limit_value_calibration_projector_deviation: Optional[float] = None
    limit_value_calibration_scale_discrepancy: Optional[float] = None
    limit_value_laser_calibration_deviation: Optional[float] = None
    limit_value_recalibration_deviation: Optional[float] = None
    max_residual_edge_point_adjustment: Optional[float] = None
    max_residual_gray_value_adjustment: Optional[float] = None
    max_z: Optional[float] = None
    measurement_temperature: Optional[float] = None
    measuring_volume_depth: Optional[float] = None
    measuring_volume_length: Optional[float] = None
    measuring_volume_width: Optional[float] = None
    min_z: Optional[float] = None
    movement_check_threshold: Optional[float] = None
    number_of_cameras: Optional[int] = None
    number_of_scales: Optional[int] = None
    object_certification_temperature: Optional[float] = None
    object_expansion_coefficient: Optional[float] = None
    object_identification_point_id: Optional[str] = None
    object_name: Optional[str] = None
    object_recertified: Optional[bool] = None
    object_type: Optional[str] = None
    original_date_draft: Optional[str] = None
    projector_deviation: Optional[float] = None
    projector_deviation_optimized: Optional[float] = None
    projector_focal_length: Optional[float] = None
    ratio_photogrammetry_exposure_time_to_distance: Optional[float] = None
    recalibration_deviation: Optional[float] = None
    recalibration_object: Optional[str] = None
    recalibration_type: Optional[str] = None
    reference_point_identification_method: Optional[str] = None
    reference_point_max_z: Optional[float] = None
    reference_point_min_z: Optional[float] = None
    reference_volume_depth: Optional[float] = None
    reference_volume_length: Optional[float] = None
    reference_volume_width: Optional[float] = None
    remaining_sensor_warmup_time: Optional[float] = None
    room_temperature: Optional[float] = None
    scale_discrepancy: Optional[float] = None
    scale_length: Optional[float] = None
    sensor_is_retro_calibrated: Optional[bool] = None
    snap_mode: Optional[str] = None
    volume_depth: Optional[float] = None
    volume_length: Optional[float] = None
    volume_width: Optional[float] = None


@dataclass
class AcquisitionMetadata:
    image_height: Optional[int] = None
    image_width: Optional[int] = None
    sensor_type: Optional[str] = None


@dataclass
class ImageModeMetadata:
    image_mode: Optional[Any] = None  # raw object if you still need it
    image_mode_camera_acquisition_mode: Optional[str] = None
    image_mode_image_area_size: Optional[Any] = None
    image_mode_image_area_size_x: Optional[float] = None
    image_mode_image_area_size_y: Optional[float] = None
    image_mode_image_area_top_left_corner: Optional[Any] = None
    image_mode_image_area_top_left_corner_x: Optional[float] = None
    image_mode_image_area_top_left_corner_y: Optional[float] = None
    image_mode_is_valid: Optional[bool] = None
    image_mode_max_measurement_frequency: Optional[float] = None
    image_mode_pixel_factor_x: Optional[float] = None
    image_mode_pixel_factor_y: Optional[float] = None


@dataclass
class SurfaceComponentParameters:
    surface_component_name: Optional[str] = None
    facet_size: Optional[int] = None
    facet_distance: Optional[int] = None
    facet_matching: Optional[Any] = None
    start_facets: Optional[Any] = None
    identify_reference_point_sizes_automatically: Optional[bool] = None
    strain_tensor_neighborhood_size: Optional[int] = None
    interpolation_size: Optional[int] = None
    definition_stage: Optional[int] = None

    computation_parameter_accuracy: Optional[float] = None
    computation_parameter_break_accuracy_linked_facets: Optional[float] = None
    computation_parameter_break_accuracy_single_facets: Optional[float] = None
    computation_parameter_max_intersection_deviation: Optional[float] = None
    computation_parameter_max_iteration_number: Optional[int] = None
    computation_parameter_max_residual: Optional[float] = None
    computation_parameter_max_sampling_points: Optional[int] = None
    computation_parameter_min_iteration_number: Optional[int] = None
    computation_parameter_min_pattern_quality: Optional[float] = None
    computation_parameter_subpixel_interpolation: Optional[bool] = None


@dataclass
class StageProcessData:
    export_date: str
    exposure_time: Optional[float]
    current_stage_index: int
    current_stage_name: Optional[str]
    current_stage_date: Optional[str]
    current_stage_date_ms: Optional[str]
    current_stage_relative_date: Optional[float]
    reference_stage_index: int
    reference_stage_name: Optional[str]
    reference_stage_date: Optional[str]


@dataclass
class RbmcData:
    alignment_is_active: bool
    alignment_rotation_x: float
    alignment_rotation_y: float
    alignment_rotation_z: float
    alignment_translation_x: float
    alignment_translation_y: float
    alignment_translation_z: float
    alignment_deviation: Optional[float]


@dataclass
class GlobalMetadata:
    process: ProcessMetadata
    calibration: CalibrationMetadata
    acquisition: AcquisitionMetadata
    image_mode: ImageModeMetadata
    surface_component: SurfaceComponentParameters


@dataclass
class PerStageMetadata:
    stage_metadata: StageObjMetadata
    stage_process_data: StageProcessData
    rbmc_data: Optional[RbmcData]
    signal_data: SignalData


@dataclass
class FacetData:
    """Data structure for facet results."""
    facet_coordinates: np.ndarray
    x_undef: np.ndarray
    y_undef: np.ndarray
    z_undef: np.ndarray
    disp_x: np.ndarray
    disp_y: np.ndarray
    disp_z: np.ndarray
    eps_x: np.ndarray
    eps_y: np.ndarray
    eps_xy: np.ndarray
    eps_eqv: np.ndarray

    @property
    def disp_norm(self) -> np.ndarray:
        """Calculate the norm of the displacement vector."""
        return np.sqrt(self.disp_x ** 2 + self.disp_y ** 2 + self.disp_z ** 2)
