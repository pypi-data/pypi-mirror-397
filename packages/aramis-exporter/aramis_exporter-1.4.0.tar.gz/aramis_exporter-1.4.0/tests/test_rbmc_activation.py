"""Integration tests covering RBMC activation/deactivation and export behaviour."""
import importlib
import tempfile
import unittest
from importlib.resources import files
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import json
from aramis_exporter.client import GOMClient
from aramis_exporter.exporter import AramisExporter, ExportConfig

DATA_DIR = files("aramis_exporter") / "test_data"
TEST_PROJECT = DATA_DIR / "aramis_projects" / "TestProjectPrepared.aramis"
FEM_RESULTS_DIR = DATA_DIR / "fem_results"
DISP_KEY = "sim_disp"
DISP_POST_KEYS = ("Top Center", "Bottom Center", "Left Center", "Right Center")
AVG_EPS_KEYS = ("avg_epto_xx", "avg_epto_yy", "avg_epto_xy")


class RbmcActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gom = importlib.import_module("gom")
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.client = GOMClient(cls.gom)
        if cls.client.project is not None:
            cls.client.close_project()
        cls.client.open_project(str(TEST_PROJECT))
        cls.reference_fem = cls._load_fem_summary()

    @classmethod
    def tearDownClass(cls):
        try:
            if getattr(cls, "client", None) and cls.client.project is not None:
                cls.client.close_project()
        finally:
            if getattr(cls, "temp_dir", None):
                cls.temp_dir.cleanup()

    @classmethod
    def _load_fem_summary(cls) -> Dict[str, Dict[str, str]]:
        payloads: Dict[str, Dict[str, str]] = {}
        for file_path in Path(FEM_RESULTS_DIR).iterdir():
            if file_path.name.endswith("_summary.json"):
                key = file_path.name.replace("_summary.json", "")
                payloads[key] = cls._read_json(file_path)
        if not payloads:
            raise AssertionError("No FEM summary files found")
        return payloads

    @staticmethod
    def _read_json(path: Path) -> Dict:
        import json

        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _build_exporter(self, *, export_folder_name: str) -> AramisExporter:
        config = ExportConfig(
            project_name="TestProject",
            specimen_name="SP",
            experiment_name="SynLoads",
            export_abs_path=str(self.temp_dir.name),
            export_folder_name=export_folder_name,
        )
        return AramisExporter(self.client, config)

    def _parse_displacements_from_file(self, path: Path) -> np.ndarray:
        header_reached = False
        values: List[List[float]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not header_reached:
                    if line.startswith("#       ID;"):
                        header_reached = True
                    continue
                if not line.strip():
                    continue
                parts = [item.strip() for item in line.split(";")]
                disp_values = [float(parts[i]) for i in range(4, 7)]
                values.append(disp_values)
        return np.asarray(values, dtype=float)

    def test_rbmc_delete_is_idempotent(self):
        self.client.initialize(set_rbmc_active=True)
        self.assertTrue(self.client._is_rbmc_applied())
        self.client._delete_rbmc()
        self.assertFalse(self.client._is_rbmc_applied())
        self.client._delete_rbmc()  # second call must be safe
        self.assertFalse(self.client._is_rbmc_applied())
        self.client._check_rbmc(activate_rbmc=False)
        self.assertFalse(self.client.rbmc_active)

    def test_exports_with_and_without_rbmc(self):
        # Export with RBMC active
        self.client.initialize(set_rbmc_active=True)
        exporter_rbmc = self._build_exporter(export_folder_name="export_with_rbmc")
        exporter_rbmc.export_data_to_txt(export_connections=False)
        nodemap_files_rbmc = sorted(exporter_rbmc.nm_subfolder_path.glob("*.txt"))
        self.assertTrue(nodemap_files_rbmc)

        # Export without RBMC
        self.client.initialize(set_rbmc_active=False)
        exporter_no_rbmc = self._build_exporter(export_folder_name="export_without_rbmc")
        exporter_no_rbmc.export_data_to_txt(export_connections=False)
        nodemap_files_no_rbmc = sorted(exporter_no_rbmc.nm_subfolder_path.glob("*.txt"))
        self.assertEqual(len(nodemap_files_rbmc), len(nodemap_files_no_rbmc))

        for with_rbmc, without_rbmc in zip(nodemap_files_rbmc, nodemap_files_no_rbmc):
            disp_with = self._parse_displacements_from_file(with_rbmc)
            disp_without = self._parse_displacements_from_file(without_rbmc)
            self.assertFalse(np.allclose(disp_with, disp_without))


if __name__ == "__main__":
    unittest.main(exit=False)
