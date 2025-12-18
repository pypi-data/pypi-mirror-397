# language: python
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

import gom
import numpy as np

from .client import GOMClient
from .models import ValueElement
from .utils import safe_asdict, safe_path


@dataclass
class ExportConfig:
    """Configuration for exporting data from Aramis.

    Attributes:
        stage_indxs: List of stage indices to export or "all" or "last". Default is "all".
        project_name: Optional project name for file naming.
        specimen_name: Optional specimen name for file naming.
        experiment_name: Optional experiment name for file naming.
        export_abs_path: Optional absolute path for export directory. Defaults to project file directory.
        export_folder_name: Optional folder name for export. Defaults to project filename + '_export'.
        export_file_name: Optional base name for export files. Defaults to project_name + specimen_name + experiment_name. If None is provided, default is project file name.
        nodemap_subfolder: Subfolder name for nodemap exports. Default is 'nodemaps'.
        connection_subfolder: Subfolder name for connection exports. Default is 'connections'.
        vtk_subfolder: Subfolder name for VTK exports. Default is 'vtk'.
    """
    stage_indxs: Union[List[int], str] = "all"
    project_name: Optional[str] = None
    specimen_name: Optional[str] = None
    experiment_name: Optional[str] = None
    export_abs_path: Optional[str] = None
    export_folder_name: Optional[str] = None
    export_file_name: Optional[str] = None
    nodemap_subfolder: str = 'nodemaps'
    connection_subfolder: str = 'connections'
    vtk_subfolder: str = 'vtk'


class AramisExporter:
    """We use this class as a HELPER module to read and export the data of an OPEN GOM Aramis Professional /
    ZEISS Inspect Pro project as a txt file in a specific format.
    You can only use this module IF YOU WORK ON YOUR GOM ARAMIS SYSTEM. And only, directly from the
    GOM Aramis scripting editor. To avoid problems, dependencies on external modules are kept to a minimum.

    Methods:
        * export_data_to_txt - export all stages to txt files or specific stages to txt files (nodemaps and/or connections)
        * export_data_to_vtk - export all stages to vtk files or specific stages to vtk files

    """

    def __init__(self, client: Union[GOMClient, Any], config: Optional[ExportConfig] = None, metadata: Dict = None,
                 logger: Optional[logging.Logger] = None, **kwargs):
        """Initializes the AramisExporter object.

        Args:
            client: GOMClient instance or gom module
            config: ExportConfig instance with export configuration
            metadata: Optional dictionary of metadata to include in exports
            logger: Optional logger instance. If None, a default logger is created.
        """
        if logger is None:
            logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
            logger.setLevel(logging.INFO)

            if not logger.hasHandlers():
                ch = logging.StreamHandler()
                ch.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    "%(asctime)s %(levelname)s %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                ch.setFormatter(formatter)
                logger.addHandler(ch)

        self.logger = logger

        # default to GOMClient if gom module is passed
        if not isinstance(client, GOMClient):
            try:
                client = GOMClient(client)
                self.logger.info("Wrapping GOM module in GOMClient...")
            except Exception as e:
                self.logger.error(f"Failed to wrap GOM module in GOMClient: {e}")
                raise
        self.client = client

        # check if client is initialized
        if not self.client.is_initialized():
            self.logger.info("Initializing GOM Client...")
            try:
                self.client.initialize()
            except Exception as e:
                self.logger.error(f"Failed to initialize GOM Client: {e}")
                raise

        # base config
        if config is None:
            config = ExportConfig()
        self.config = config

        # legacy kwargs support
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                self.logger.info(f"Overwriting config attribute '{key}' with value from kwargs.")
                self.logger.info("Note: Passing config attributes via kwargs is deprecated. Use ExportConfig instead.")

        if "metadata_dict" in kwargs and metadata is None:
            metadata = kwargs["metadata_dict"]
            self.logger.info("Using 'metadata_dict' from kwargs as metadata.")
            self.logger.info("Note: Passing metadata via 'metadata_dict' is deprecated. Use 'metadata' parameter instead.")

        # metadata
        self.ref_stage = self.client.get_ref_stage_index()
        self.project_metadata = self.client.get_project_metadata()
        self.config_metadata = safe_asdict(self.config)
        self.custom_metadata = metadata

        # file & folder names
        self.export_file_name = self._construct_file_name_prefix()
        self.export_folder_name = self.config.export_folder_name or self.client.get_project_name() + "_export"
        self.nm_folder_name = self.config.nodemap_subfolder
        self.conn_folder_name = self.config.connection_subfolder
        self.vtk_folder_name = self.config.vtk_subfolder

        # Paths
        self.export_abs_path = safe_path(self.config.export_abs_path) or safe_path(
            self.client.get_project_file_path()).parent
        self.export_folder_path = safe_path(self.export_abs_path, self.export_folder_name)
        self.nm_subfolder_path = self.export_folder_path / self.config.nodemap_subfolder
        self.conn_subfolder_path = self.export_folder_path / self.conn_folder_name
        self.vtk_subfolder_path = self.export_folder_path / self.vtk_folder_name

    def export_data(self,
                    stage_indxs: Union[List[int], str] = "all",
                    export_abs_path: str = None,
                    export_folder_name: str = None,
                    nodemap_subfolder: str = 'nodemaps',
                    connection_subfolder: str = 'connections'
                    ):
        """Legacy method to export data to txt files."""
        self.logger.warning("export_data is deprecated. The method will be removed in future version."
                            "Please use export_data_to_txt instead.")
        self.export_data_to_txt(stage_indxs=stage_indxs,
                                export_abs_path=export_abs_path,
                                export_folder_name=export_folder_name,
                                nm_subfolder_name=nodemap_subfolder,
                                conn_subfolder_name=connection_subfolder,
                                export_connections=True)

    def export_data_to_txt(self,
                           stage_indxs: Optional[Union[List[int], str]] = None,
                           export_abs_path: Optional[str] = None,
                           export_folder_name: Optional[str] = None,
                           nm_subfolder_name: Optional[str] = None,
                           conn_subfolder_name: Optional[str] = None,
                           export_connections: bool = True,
                           ):
        """Can be called to export all stages to txt files or specific stages to txt files.

        Args:
            stage_indxs: Optional list of stage indices to export or "all" or "last". Overrides config if provided.
            export_abs_path: Optional absolute path for export directory. Overrides config if provided.
            export_folder_name: Optional folder name for export. Overrides config if provided.
            nm_subfolder_name: Optional subfolder name for nodemap exports. Overrides config if provided.
            conn_subfolder_name: Optional subfolder name for connection exports. Overrides config if provided.
            export_connections: Whether to export connection files alongside nodemaps. Defaults to True.
        """
        self.logger.info("Starting nodemap and connection export...")
        self.logger.info("Checking export configuration...")

        self._prepare_export_folders(export_abs_path=export_abs_path, export_folder_name=export_folder_name,
                                     nodemaps=nm_subfolder_name, connections=conn_subfolder_name, make_vtk=False)

        stages = self._get_export_stages(stage_indxs=stage_indxs)

        self.logger.info(f'Number of stages {len(stages)}')
        start_time = time.time()
        for i, current_stage in enumerate(stages):
            current_stage_index = self.client.get_index_of_stage(current_stage)
            self._log_stage_progress(i, len(stages), current_stage_index, start_time)
            self.client.show_stage(stage_idx=current_stage_index) # important to load the stage data
            if self.client.is_current_stage_computed:
                self._export_stage_to_txt(nodemap_export_directory=self.nm_subfolder_path,
                                          connection_export_directory=self.conn_subfolder_path,
                                          export_connections=export_connections)

    def export_data_to_vtk(self,
                           stage_indxs: Optional[Union[List[int], str]] = None,
                           export_abs_path: Optional[str] = None,
                           export_folder_name: Optional[str] = None,
                           vtk_subfolder: Optional[str] = None,
                           ):

        """
        Can be called to export all stages to vtk files or specific stages to vtk files.

        Args:
            stage_indxs: Optional list of stage indices to export or "all" or "last". Overrides config if provided.
            export_abs_path: Optional absolute path for export directory. Overrides config if provided.
            export_folder_name: Optional folder name for export. Overrides config if provided.
            vtk_subfolder: Optional subfolder name for VTK exports. Overrides config if provided
        """
        #TODO: Kwargs naming consistency with other export methods (vtk_subfolder -> vtk_subfolder_name)
        # when old export_data is removed

        self.logger.info("Starting VTK export...")
        self.logger.info("Checking export configuration...")

        self._prepare_export_folders(export_abs_path=export_abs_path, export_folder_name=export_folder_name,
                                     vtk=vtk_subfolder, make_nm=False, make_conn=False)

        stages = self._get_export_stages(stage_indxs=stage_indxs)

        start_time = time.time()
        self.logger.info(f'Number of stages {len(stages)}')
        for i, current_stage in enumerate(stages):
            current_stage_index = self.client.get_index_of_stage(current_stage)
            self._log_stage_progress(i, len(stages), current_stage_index, start_time)
            self.client.show_stage(stage_idx=current_stage_index)
            if self.client.is_current_stage_computed:
                self._export_stage_to_vtk(export_directory=self.vtk_subfolder_path)

    def _log_stage_progress(self, idx: int, total: int, stage_index: int, start_time: float):
        """Logs the progress of stage export.

        Args:
            idx: current index in the loop
            total: total number of stages
            stage_index: index of the current stage
            start_time: time when the export started

        """
        percent_complete = (idx + 1) / total * 100
        elapsed = time.time() - start_time
        avg_per_stage = elapsed / max(1, (idx + 1))
        remaining = max(0, total - (idx + 1))
        eta_seconds = remaining * avg_per_stage
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
        finish_ts = datetime.now() + timedelta(seconds=eta_seconds)
        self.logger.info(
            f"Exporting stage {stage_index} ({idx + 1}/{total}, {percent_complete:.2f}%) - ETA {eta_str} (finish {finish_ts:%H:%M:%S})")

    def _export_stage_to_txt(self, nodemap_export_directory: Path, connection_export_directory: Path,
                             export_connections: bool = True):
        """Exports exactly one stage to txt.

        Args:
            nodemap_export_directory: relative path to nodemap export directory
            connection_export_directory: relative path to connection export directory
            export_connections: Whether to export connection file alongside nodemap. Defaults to True.

        """
        start = time.time()
        current_stage_index = self.client.get_current_stage_index()
        self.logger.info(f"Exporting stage with index {current_stage_index} in...")
        # getting the current stage as object

        out_file_name = f"{self.export_file_name}_dic_results_{self.ref_stage}_{current_stage_index}"

        out_file = open(Path(nodemap_export_directory) / f"{out_file_name}.txt", 'w')
        self._write_header(out_file)
        self._write_nodemap(out_file)
        out_file.close()

        if export_connections:
            connection_file_name = out_file_name + "_connections"
            connection_file = open(Path(connection_export_directory) / f"{connection_file_name}.txt", 'w')
            self._write_connections(connection_file)

            connection_file.close()

        time_taken = time.time() - start
        self.logger.info(f"Export time: {time_taken:.2f} seconds")

    def _write_header(self, out_file):
        """Adds a header of metadata to an nodemap output file.

        Args:
            out_file: (open file object) Output file which should get the header
        """

        # Find the max key length for all header sections for perfect alignment
        project_meta = self.project_metadata
        stage_meta = self.client.get_current_stage_metadata()

        all_keys = []
        for section in [safe_asdict(project_meta), safe_asdict(stage_meta)]:
            for key, value in section.items():
                if isinstance(value, dict):
                    all_keys += list(value.keys())
                else:
                    all_keys.append(key)

        max_key_len = max(len(str(k)) for k in all_keys) if all_keys else 36
        pad = max(36, max_key_len + 2)

        def aligned_kv_line(key, value):
            return f"# {str(key).ljust(pad)}: {str(value)}\n"

        def write_metadata_section(out_file, title, dataclass_obj):
            out_file.write(f"# {title}:\n")
            d = safe_asdict(dataclass_obj) if hasattr(dataclass_obj, '__dataclass_fields__') else dataclass_obj
            if d is None or len(d) == 0:
                out_file.write("#" * 100 + "\n")
                return
            for key, value in d.items():
                out_file.write(aligned_kv_line(key, value))
            out_file.write("#" * 100 + "\n")

        def write_value_elements(out_file, element_list: List[ValueElement], title=None):
            if title:
                out_file.write(f"# {title}:\n")
            if element_list is None or len(element_list) == 0:
                return
            for ele in element_list:
                key = ele.name
                val = f"{str(ele.type).ljust(20)}: {str(ele.value)}"
                out_file.write(aligned_kv_line(key, val))
            out_file.write('#\n')

        # write global metadata
        write_metadata_section(out_file, "Export configuration", self.config_metadata)
        write_metadata_section(out_file, "Custom metadata", self.custom_metadata)
        write_metadata_section(out_file, "Process data", project_meta.process)
        write_metadata_section(out_file, "Camera information", project_meta.acquisition)
        write_metadata_section(out_file, "Image mode", project_meta.image_mode)
        write_metadata_section(out_file, "Calibration information", project_meta.calibration)
        write_metadata_section(out_file, "Surface component", project_meta.surface_component)
        # write per-stage metadata
        write_metadata_section(out_file, "Stage process data", stage_meta.stage_process_data)
        write_metadata_section(out_file, "rigid body motion compensation", stage_meta.rbmc_data)
        # write signal value elements
        signals = stage_meta.signal_data
        write_value_elements(out_file, signals.inspection_value_elements, "SIGNALS")
        write_value_elements(out_file, signals.value_elements)
        write_value_elements(out_file, signals.analog_inputs)
        out_file.write("#" * 100 + "\n")

    def _write_nodemap(self, out_file):
        """Adds facet data to an output file.

        Args:
            out_file: (open file object) Output file which should get the header
        """

        facet_data = self.client.get_current_stage_results()
        out_file.write(
            f'#{"ID":>9}; {"x_undef [mm]":>20}; {"y_undef [mm]":>20}; {"z_undef [mm]":>20}; '
            f'{"u [mm]":>20}; {"v [mm]":>20}; {"w [mm]":>20}; '
            f'{"epsx [%]":>20}; {"epsy [%]":>20}; {"epsxy [1]":>20}; {"epseqv [%]":>20}\n'
        )

        for facet_index in range(len(facet_data.facet_coordinates[:, 0])):
            out_file.write(
                f'{facet_index + 1:10.0f}; '
                f'{facet_data.x_undef[facet_index]:20.10f}; '
                f'{facet_data.y_undef[facet_index]:20.10f}; '
                f'{facet_data.z_undef[facet_index]:20.10f}; '
                f'{facet_data.disp_x[facet_index]:20.15f}; '
                f'{facet_data.disp_y[facet_index]:20.15f}; '
                f'{facet_data.disp_z[facet_index]:20.15f}; '
                f'{facet_data.eps_x[facet_index]:20.15f}; '
                f'{facet_data.eps_y[facet_index]:20.15f}; '
                f'{facet_data.eps_xy[facet_index]:20.15f}; '
                f'{facet_data.eps_eqv[facet_index]:20.15f}\n'
            )

    def _write_connections(self, connection_file):
        """Internal routine to write a connection file, i.e. triangular connection of facets' center points.

        Args:
            connection_file: (open file object) Output file which should get the header

        """
        connection_file.write(
            f'{"Type":>10}; {"Element #":>10}; {"Node 1":>10}; {"Node 2":>10}; {"Node 3":>10}\n')

        connection_array = self.client.get_current_stage_facet_connections()
        for elem in range(len(connection_array[:, 0])):
            connection_file.write(
                f' {3:>10}; {elem + 1:>10}; {connection_array[elem, 0]:>10}; '
                f'{connection_array[elem, 1]:>10}; {connection_array[elem, 2]:>10}\n'
            )

    def _export_stage_to_vtk(self, export_directory: Path):
        """Exports exactly one stage to vtk.

        Args:
            export_directory: relative path to export directory
            current_stage_index: index of stage to be exported

        """
        start = time.time()
        current_stage_index = self.client.get_current_stage_index()
        self.logger.info(f"Exporting to vtk stage with index {current_stage_index} in...")
        # getting the current stage as object
        vtk_file_name = f"{self.export_file_name}_{self.ref_stage}_{current_stage_index}"

        with open(Path(export_directory) / f"{vtk_file_name}.vtk", 'w') as vtk_file:
            vtk_file.write("# vtk DataFile Version 2.0\n"
                           "3D unstructured mesh of FE model with tetra elements\n"
                           "ASCII\n"
                           "\n"
                           "DATASET UNSTRUCTURED_GRID\n")
            self._write_data_to_vtk(vtk_file, current_stage_idx=current_stage_index)

        time_taken = time.time() - start
        self.logger.info(f"Export time: {time_taken:.2f} seconds")

    def _write_data_to_vtk(self, vtk_file, current_stage_idx: int):
        """Internal routine to fill an open .vtk file.

        Args:
            vtk_file: (open file object) Output .vtk file
            current_stage_idx: number of current stage

        """
        facet_data = self.client.get_current_stage_results()
        triangle_connections = self.client.get_current_stage_facet_connections()

        vtk_file.write(f'POINTS {len(facet_data.x_undef[:])} float\n')
        for point_index in range(len(facet_data.x_undef[:])):
            if np.isnan(facet_data.x_undef[point_index]):
                vtk_file.write('0 0 0\n')
            else:
                vtk_file.write(
                    f'{facet_data.x_undef[point_index]} '
                    f'{facet_data.y_undef[point_index]} '
                    f'{facet_data.z_undef[point_index]}\n')

        # get missing triangles
        no_of_missing_cells = 0
        for element_index in range(len(triangle_connections[:, 0])):
            if triangle_connections[element_index, 0] == -1:
                no_of_missing_cells += 1
            else:
                pass

        vtk_file.write('\n')
        vtk_file.write(
            f'CELLS {len(triangle_connections[:, 0]) - no_of_missing_cells} '
            f'{4 * (len(triangle_connections[:, 0]) - no_of_missing_cells)}\n')

        for elem in range(len(triangle_connections[:, 0])):
            if triangle_connections[elem, 0] == -1:
                pass
            else:
                vtk_file.write(
                    f'3 {triangle_connections[elem, 0]} '
                    f'{triangle_connections[elem, 1]} '
                    f'{triangle_connections[elem, 2]}\n')

        vtk_file.write('\n')
        vtk_file.write(f'CELL_TYPES {len(triangle_connections[:, 0]) - no_of_missing_cells}\n')
        for _ in range(len(triangle_connections[:, 0]) - no_of_missing_cells):
            vtk_file.write('5\n')

        # point data
        vtk_file.write(f'POINT_DATA {len(facet_data.x_undef)}\n')
        self._write_scalar_to_vtk(vtk_file, 'x%20[mm]', facet_data.x_undef)
        self._write_scalar_to_vtk(vtk_file, 'y%20[mm]', facet_data.y_undef)
        self._write_scalar_to_vtk(vtk_file, 'z%20[mm]', facet_data.z_undef)
        self._write_scalar_to_vtk(vtk_file, 'u_x%20[mm]', facet_data.disp_x)
        self._write_scalar_to_vtk(vtk_file, 'u_y%20[mm]', facet_data.disp_y)
        self._write_scalar_to_vtk(vtk_file, 'u_z%20[mm]', facet_data.disp_z)
        self._write_scalar_to_vtk(vtk_file, 'u_sum%20[mm]', facet_data.disp_norm)
        self._write_scalar_to_vtk(vtk_file, 'eps_x%20[%25]', facet_data.eps_x)
        self._write_scalar_to_vtk(vtk_file, 'eps_y%20[%25]', facet_data.eps_y)
        self._write_scalar_to_vtk(vtk_file, 'eps_xy%20[1]', facet_data.eps_xy)
        self._write_scalar_to_vtk(vtk_file, 'eps_vm%20[%25]', facet_data.eps_eqv)

    def _write_scalar_to_vtk(self, vtk_file, scalar_name: str, scalar_data: np.ndarray):
        """Internal routine to write a scalar to an open .vtk file.

        Args:
            vtk_file: (open file object) Output .vtk file
            scalar_name: name of the scalar
            scalar_data: np.array of scalar data

        """
        vtk_file.write(f'SCALARS {scalar_name} float\n')
        vtk_file.write('LOOKUP_TABLE default\n')
        for point_index in range(len(scalar_data)):
            if np.isnan(scalar_data[point_index]):
                vtk_file.write('0.0\n')
            else:
                vtk_file.write(f'{scalar_data[point_index]}\n')

    def _construct_file_name_prefix(self):
        """Constructs the file name prefix based on the configuration.

        Returns:
            str: The constructed file name prefix.
        """
        if self.config.export_file_name:
            return self.config.export_file_name

        prefix_parts = []
        if self.config.project_name:
            prefix_parts.append(self.config.project_name)
        if self.config.specimen_name:
            prefix_parts.append(self.config.specimen_name)
        if self.config.experiment_name:
            prefix_parts.append(self.config.experiment_name)
        return "_".join(prefix_parts) if prefix_parts else self.client.get_project_name()

    def _prepare_export_folders(
            self,
            export_abs_path: Optional[str] = None,
            export_folder_name: Optional[str] = None,
            nodemaps: Optional[str] = None,
            connections: Optional[str] = None,
            vtk: Optional[str] = None,
            make_nm = True,
            make_conn = True,
            make_vtk = True,
    ):
        """Prepares export subfolders for nodemaps, connections, and VTK files.

        Args:
            export_abs_path: Base path for exports. Overrides config if provided.
            export_folder_name: Optional folder name for exports. Overrides config if provided.
            nodemaps: Optional subfolder name for nodemap exports. Overrides config if provided.
            connections: Optional subfolder name for connection exports. Overrides config if provided.
            vtk: Optional subfolder name for VTK exports. Overrides config if provided.
        """
        if export_abs_path is not None:
            self.export_abs_path = safe_path(export_abs_path)
        if export_folder_name is not None:
            self.export_folder_name = export_folder_name

        self.export_folder_path = safe_path(self.export_abs_path, self.export_folder_name)
        self.logger.info(f"Export folder path is set to {self.export_folder_path}")

        if nodemaps is not None:
            self.nm_folder_name = nodemaps
            self.nm_subfolder_path = safe_path(self.export_folder_path, self.nm_folder_name)
            self.logger.info(f"Overwriting nm_subfolder_path with {self.nm_subfolder_path}")
        if connections is not None:
            self.conn_folder_name = connections
            self.conn_subfolder_path = safe_path(self.export_folder_path, self.conn_folder_name)
            self.logger.info(f"Overwriting conn_subfolder_path with {self.conn_subfolder_path}")
        if vtk is not None:
            self.vtk_folder_name = self.vtk_folder_name
            self.vtk_subfolder_path = safe_path(self.export_folder_path, self.vtk_folder_name)
            self.logger.info(f"Overwriting vtk_subfolder_path with {self.vtk_folder_name}")

        for name, path, make in [('nodemap', self.nm_subfolder_path, make_nm),
                           ('connection', self.conn_subfolder_path, make_conn),
                           ('vtk', self.vtk_subfolder_path, make_vtk)]:
            if not path.exists() and make:
                path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created {name} export folder at {str(path)}.")
            elif path.exists() and make:
                self.logger.info(f"{name.capitalize()} export folder exists at {str(path)}.")
            else:
                continue

    def _get_export_stages(self, stage_indxs: Optional[Union[List[int], str]] = None) -> List[Any]:
        """Determines which stages to export based on the configuration.

        Args:
            stage_indxs: Optional list of stage indices to export or "all" or "last". Overrides config if provided.

        Returns:
            List[Any]: List of stages to export.
        """
        if stage_indxs is not None:
            self.logger.info("Overriding stage indices from method argument.")
            self.config.stage_indxs = stage_indxs

        if self.config.stage_indxs == "all":
            self.logger.info("Exporting all stages as per configuration.")
            return self.client.get_all_stages()
        elif self.config.stage_indxs == "last":
            self.logger.info("Exporting last stage as per configuration.")
            return [self.client.get_all_stages()[-1]]
        else:
            stages = [self.client.get_stage_by_index(i) for i in self.config.stage_indxs]
            self.logger.info(f"Exporting specified stages: {self.config.stage_indxs} as per configuration.")
            return [s for s in stages if s is not None]


