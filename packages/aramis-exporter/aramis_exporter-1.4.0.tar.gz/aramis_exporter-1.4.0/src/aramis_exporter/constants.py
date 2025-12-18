"""Constants for the Aramis Exporter module."""

# Mapping of gom result type extensions to standardized result type names
RESULT_TYPE_MAP = {".epsX": "epsilon_x",
       ".epsY": "epsilon_y",
       ".epsXY": "epsilon_xy",
       ".phiM": "mises_strain",
       ".dX": "displacement",
       ".dY": "displacement",
       ".dZ": "displacement"
       }

# Mapping of gom displacement extensions to coordinate directions
DISP_DIRECTION_MAP = {".dX": "x",
                   ".dY": "y",
                   ".dZ": "z"
                   }

# Mapping of gom paths to CalibrationMetadata fields
CALIBRATION_FIELD_MAP = {
    "camera_angle": "camera_angle",
    "camera_focal_length": "camera_focal_length",
    "calibration_date": "date",
    "calibration_deviation": "deviation",
    "deviation_optimized": "deviation_optimized",
    "height_variance": "height_variance",
    "is_overexposure_check_ignored": "is_overexposure_check_ignored",
    "is_quick_calibrated": "is_quick_calibrated",
    "laser_calibration_deviation": "laser_calibration_deviation",
    "light_intensity": "light_intensity",
    "limit_value_calibration_deviation": "limit_value_calibration_deviation",
    "limit_value_calibration_projector_deviation": "limit_value_calibration_projector_deviation",
    "limit_value_calibration_scale_discrepancy": "limit_value_calibration_scale_discrepancy",
    "limit_value_laser_calibration_deviation": "limit_value_laser_calibration_deviation",
    "limit_value_recalibration_deviation": "limit_value_recalibration_deviation",
    "max_residual_edge_point_adjustment": "max_residual_edge_point_adjustment",
    "max_residual_gray_value_adjustment": "max_residual_gray_value_adjustment",
    "max_z": "max_z",
    "measurement_temperature": "measurement_temperature",
    "measuring_volume_depth": "measuring_volume_depth",
    "measuring_volume_length": "measuring_volume_length",
    "measuring_volume_width": "measuring_volume_width",
    "min_z": "min_z",
    "movement_check_threshold": "movement_check_threshold",
    "number_of_cameras": "number_of_cameras",
    "number_of_scales": "number_of_scales",
    "object_certification_temperature": "object_certification_temperature",
    "object_expansion_coefficient": "object_expansion_coefficient",
    "object_identification_point_id": "object_identification_point_id",
    "object_name": "object_name",
    "object_recertified": "object_recertified",
    "object_type": "object_type",
    "original_date_draft": "original_date_draft",
    "projector_deviation": "projector_deviation",
    "projector_deviation_optimized": "projector_deviation_optimized",
    "projector_focal_length": "projector_focal_length",
    "ratio_photogrammetry_exposure_time_to_distance": "ratio_photogrammetry_exposure_time_to_distance",
    "recalibration_deviation": "recalibration_deviation",
    "recalibration_object": "recalibration_object",
    "recalibration_type": "recalibration_type",
    "reference_point_identification_method": "reference_point_identification_method",
    "reference_point_max_z": "reference_point_max_z",
    "reference_point_min_z": "reference_point_min_z",
    "reference_volume_depth": "reference_volume_depth",
    "reference_volume_length": "reference_volume_length",
    "reference_volume_width": "reference_volume_width",
    "remaining_sensor_warmup_time": "remaining_sensor_warmup_time",
    "room_temperature": "room_temperature",
    "scale_discrepancy": "scale_discrepancy",
    "scale_length": "scale_length",
    "sensor_is_retro_calibrated": "sensor_is_retro_calibrated",
    "snap_mode": "snap_mode",
    "volume_depth": "volume_depth",
    "volume_length": "volume_length",
    "volume_width": "volume_width",
}

# Mapping of gom paths to ImageModeMetadata fields
ACQUISITION_FIELD_MAP = {
    "image_height": "image_height",
    "image_width": "image_width",
    "sensor_type": "sensor_type",
}

# Mapping of gom paths to AcquisitionMetadata fields
IMAGE_MODE_FIELD_MAP = {
    "image_mode_camera_acquisition_mode": "camera_acquisition_mode",
    "image_mode_image_area_size": "image_area_size",
    "image_mode_image_area_size_x": "image_area_size.x",
    "image_mode_image_area_size_y": "image_area_size.y",
    "image_mode_image_area_top_left_corner": "image_area_top_left_corner",
    "image_mode_image_area_top_left_corner_x": "image_area_top_left_corner.x",
    "image_mode_image_area_top_left_corner_y": "image_area_top_left_corner.y",
    "image_mode_is_valid": "is_valid",
    "image_mode_max_measurement_frequency": "max_measurement_frequency",
    "image_mode_pixel_factor_x": "pixel_factor_x",
    "image_mode_pixel_factor_y": "pixel_factor_y",
}

SURFACE_COMPONENT_FIELD_MAP = {
    "surface_component_name": "name",
    "facet_size": "facet_size",
    "facet_distance": "point_distance",
    "facet_matching": "facet_matching",
    "start_facets": "start_facets",
    "identify_reference_point_sizes_automatically": "identify_reference_point_sizes_automatically",
    "strain_tensor_neighborhood_size": "strain_tensor_neighborhood",
    "interpolation_size": "interpolation_size",
    "definition_stage": "definition_stage",

    "computation_parameter_accuracy": "computation_parameter.accuracy",
    "computation_parameter_break_accuracy_linked_facets": "computation_parameter.break_accuracy_linked_facets",
    "computation_parameter_break_accuracy_single_facets": "computation_parameter.break_accuracy_single_facets",
    "computation_parameter_max_intersection_deviation": "computation_parameter.max_intersection_deviation",
    "computation_parameter_max_iteration_number": "computation_parameter.max_iteration_number",
    "computation_parameter_max_residual": "computation_parameter.max_residual",
    "computation_parameter_max_sampling_points": "computation_parameter.max_sampling_points",
    "computation_parameter_min_iteration_number": "computation_parameter.min_iteration_number",
    "computation_parameter_min_pattern_quality": "computation_parameter.min_pattern_quality",
    "computation_parameter_subpixel_interpolation": "computation_parameter.subpixel_interpolation",
}

