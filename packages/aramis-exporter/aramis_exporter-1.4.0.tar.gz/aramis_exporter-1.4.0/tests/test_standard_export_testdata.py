"""Stdlib unittests for exporter workflows using the prepared project."""
import importlib
import sys
import tempfile
import unittest
from importlib.resources import files

from aramis_exporter.client import GOMClient
from aramis_exporter.exporter import AramisExporter, ExportConfig

DATA_DIR = files("aramis_exporter") / "test_data"
TEST_PROJECT = DATA_DIR / "aramis_projects" / "TestProjectPrepared.aramis"


class GomModulePreparedTests(unittest.TestCase):
    def test_gom_module_available(self):
        self.assertIn("gom", sys.modules)

    def test_gom_import(self):
        module = importlib.import_module("gom")
        self.assertTrue(hasattr(module, "app"))
        self.assertTrue(hasattr(module, "script"))


class PreparedProjectClientTests(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")
        self.client = GOMClient(self.gom)
        if self.client.project is not None:
            self.client.close_project()
        self.client.open_project(str(TEST_PROJECT))

    def test_initialization_and_metadata(self):
        self.client.initialize()
        self.assertTrue(self.client.is_initialized())
        self.assertIsNotNone(self.client.get_project_metadata())

    def test_show_stage_and_results(self):
        self.client.initialize()
        stage = self.client.show_stage(0)
        self.assertEqual(stage.get("index"), 0)
        data = self.client.get_current_stage_results()
        self.assertIsNotNone(data)


class PreparedExporterLegacyTests(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")
        self.temp_dir = tempfile.TemporaryDirectory()
        client = GOMClient(self.gom)
        if client.project is not None:
            client.close_project()
        client.open_project(str(TEST_PROJECT))
        self.exporter = AramisExporter(client,
                                       project_name="TestProject",
                                       specimen_name="SP",
                                       experiment_name="SynLoads")

    def test_legacy_export_flow(self):
        self.exporter.export_data(stage_indxs="all",
                                  export_abs_path=str(self.temp_dir.name),
                                  nodemap_subfolder="custom_nodemap_folder",
                                  connection_subfolder="custom_connection_subfolder")
        nodemap_files = list(self.exporter.nm_subfolder_path.glob("*.txt"))
        ref_stage_idx = self.exporter.client.get_ref_stage_index()
        self.assertTrue(nodemap_files)
        for file in nodemap_files:
            self.assertTrue(file.name.startswith(
                f"TestProject_SP_SynLoads_dic_results_{ref_stage_idx}_"))

    def tearDown(self):
        self.temp_dir.cleanup()


class PreparedExporterConfigTests(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")
        self.temp_dir = tempfile.TemporaryDirectory()
        client = GOMClient(self.gom)
        if client.project is not None:
            client.close_project()
        client.open_project(str(TEST_PROJECT))
        self.config = ExportConfig(project_name="TestProject",
                                   specimen_name="SP",
                                   experiment_name="SynLoads",
                                   export_abs_path=str(self.temp_dir.name),
                                   export_folder_name="TestProjectFolder",
                                   export_file_name="CustomFileName",
                                   nodemap_subfolder="custom_nodemap_folder",
                                   connection_subfolder="custom_connection_folder",
                                   vtk_subfolder="custom_vtk_folder",
                                   )
        self.exporter = AramisExporter(client, self.config)

    def test_full_config_flow(self):
        ref_stage_idx = self.exporter.client.get_ref_stage_index()
        self.exporter.export_data_to_txt()
        nodemap_files = list(self.exporter.nm_subfolder_path.glob("*.txt"))
        self.assertTrue(nodemap_files)
        for file in nodemap_files:
            self.assertTrue(file.name.startswith(f"{self.config.export_file_name}_dic_results_{ref_stage_idx}_"))
        connection_files = list(self.exporter.conn_subfolder_path.glob("*.txt"))
        self.assertTrue(connection_files)
        for file in connection_files:
            self.assertTrue(file.name.startswith(f"{self.config.export_file_name}_dic_results_{ref_stage_idx}_"))
        self.exporter.export_data_to_vtk()
        vtk_files = list(self.exporter.vtk_subfolder_path.glob("*.vtk"))
        self.assertTrue(vtk_files)
        for file in vtk_files:
            self.assertTrue(file.name.startswith(f"{self.config.export_file_name}_{ref_stage_idx}_"))

    def tearDown(self):
        self.temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main(exit=False)
