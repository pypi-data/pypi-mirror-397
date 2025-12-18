"""Stdlib unittests for the exporter workflows using an already opened project."""
import importlib
import sys
import tempfile
import unittest

from aramis_exporter.client import GOMClient
from aramis_exporter.exporter import AramisExporter, ExportConfig

class GomModuleTests(unittest.TestCase):
    def test_gom_module_available(self):
        self.assertIn("gom", sys.modules)

    def test_gom_import(self):
        module = importlib.import_module("gom")
        self.assertTrue(hasattr(module, "app"))
        self.assertTrue(hasattr(module, "script"))


class GomClientTests(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")

    def test_initialization_and_metadata(self):
        client = GOMClient(self.gom)
        client.initialize()
        self.assertTrue(client.is_initialized())
        self.assertIsNotNone(client.get_project_metadata())

    def test_show_stage_and_results(self):
        client = GOMClient(self.gom)
        client.initialize()
        stage = client.show_stage(0)
        self.assertEqual(stage.get('index'), 0)
        data = client.get_current_stage_results()
        self.assertIsNotNone(data)


class ExporterLegacyTests(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")
        self.temp_dir = tempfile.TemporaryDirectory()

    def test_legacy_export_flow(self):
        exporter = AramisExporter(self.gom,
                                   project_name="Legacy",
                                   specimen_name="SP01",
                                   experiment_name="EXP")
        exporter.export_data(stage_indxs='all',
                             export_abs_path=str(self.temp_dir.name))
        nodemap_files = list(exporter.nm_subfolder_path.glob('*.txt'))
        self.assertTrue(nodemap_files)
        # assert startswith legacy filename
        for file in nodemap_files:
            self.assertTrue(file.name.startswith("Legacy_SP01_EXP_dic_results_"))

    def tearDown(self):
        self.temp_dir.cleanup()


class ExporterConfigTests(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")
        self.temp_dir = tempfile.TemporaryDirectory()

    def test_full_config_flow(self):
        config = ExportConfig(project_name="Proj", specimen_name="Spec", experiment_name="123",
                              export_abs_path=str(self.temp_dir.name))
        exporter = AramisExporter(self.gom, config)
        exporter.export_data_to_txt()
        nodemap_files = list(exporter.nm_subfolder_path.glob('*.txt'))
        self.assertTrue(nodemap_files)
        for file in nodemap_files:
            self.assertTrue(file.name.startswith("Proj_Spec_123_dic_results_"))
        exporter.export_data_to_vtk()
        vtk_files = list(exporter.vtk_subfolder_path.glob('*.vtk'))
        self.assertTrue(vtk_files)
        for file in vtk_files:
            self.assertTrue(file.name.startswith("Proj_Spec_123_dic_results_"))

    def tearDown(self):
        self.temp_dir.cleanup()


class ExporterConfigTestWithClient(unittest.TestCase):
    def setUp(self):
        self.gom = importlib.import_module("gom")
        self.client = GOMClient(self.gom)
        self.client.initialize()
        self.temp_dir = tempfile.TemporaryDirectory()

    def test_config_with_client_flow(self):
        config = ExportConfig(project_name="ClientProj", specimen_name="ClientSpec",
                              experiment_name="456", export_abs_path=str(self.temp_dir.name))
        exporter = AramisExporter(self.client, config)
        exporter.export_data_to_txt()
        nodemap_files = list(exporter.nm_subfolder_path.glob('*.txt'))
        self.assertTrue(nodemap_files)
        for file in nodemap_files:
            self.assertTrue(file.name.startswith("ClientProj_ClientSpec_456_dic_results_"))

    def tearDown(self):
        self.temp_dir.cleanup()


if __name__ == '__main__':
    unittest.main(exit=False)
