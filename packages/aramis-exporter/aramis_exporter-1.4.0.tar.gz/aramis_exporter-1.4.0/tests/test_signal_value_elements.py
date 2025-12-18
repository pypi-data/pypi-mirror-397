"""Tests for signal value elements and nodemap metadata."""
import importlib
from importlib.resources import files
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

from aramis_exporter.client import GOMClient
from aramis_exporter.exporter import AramisExporter, ExportConfig

DATA_DIR = files("aramis_exporter") / "test_data"
TEST_PROJECT = DATA_DIR / "aramis_projects" / "TestProjectPrepared.aramis"
BASE_CONFIG = ExportConfig(project_name="TestProject", specimen_name="SP", experiment_name="SynLoads")
VALUE_KEYS = ("project_name", "specimen_name", "exp_number")
STRESS_KEYS = ("s_xx", "s_yy", "s_xy")


class SignalValueElementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gom = importlib.import_module("gom")
        cls.client = GOMClient(cls.gom)
        if cls.client.project is not None:
            cls.client.close_project()
        cls.client.open_project(str(TEST_PROJECT))
        cls.client.initialize()
        cls.stage_signals = cls._collect_stage_signals()

    @classmethod
    def tearDownClass(cls):
        cls.client.close_project()

    @classmethod
    def _collect_stage_signals(cls) -> Dict[int, Dict[str, object]]:
        stage_payload = {}
        num_stages = cls.client.get_num_stages()
        ref_stage = cls.client.get_ref_stage_index()
        for stage_idx in range(num_stages):
            cls.client.show_stage(stage_idx)
            metadata = cls.client.get_current_stage_metadata()
            stage_name = cls.client.project.stages[stage_idx].get("name")
            stage_payload[stage_idx] = {
                "name": stage_name,
                "signals": cls._signal_elements_to_dict(metadata.signal_data),
                "is_ref" : bool(stage_idx == ref_stage)
            }
        return stage_payload

    @staticmethod
    def _signal_elements_to_dict(signal_data) -> Dict[str, object]:
        data = {}
        if signal_data is None:
            return data
        collections: List = [signal_data.inspection_value_elements,
                             signal_data.value_elements,
                             signal_data.analog_inputs]
        for collection in collections:
            if not collection:
                continue
            for element in collection:
                data[element.name] = element.value
        return data

    @staticmethod
    def _extract_stage_components(stage_name: str) -> List[float]:
        if not stage_name:
            return []
        # split by underscores and convert to float
        parts = stage_name.split("_")
        # get the first 3 parts that can be converted to float -> naming convention here  for s_xx, s_yy, s_xy
        components = []
        for part in parts:
            try:
                value = float(part)
                components.append(value)
            except ValueError:
                continue
            if len(components) >= 3:
                break
        # check if we found the 3 components, if not its probably the reference stage
        if len(components) < 3:
            return []
        return components

    @staticmethod
    def _extract_stage_index_from_filename(file_path: Path) -> int:
        stem_parts = file_path.stem.split("_")
        if not stem_parts:
            raise AssertionError(f"Unexpected nodemap file name: {file_path.name}")
        return int(stem_parts[-1])

    @staticmethod
    def _read_signals_block(file_path: Path) -> Dict[str, str]:
        signals = {}
        in_block = False
        with file_path.open("r", encoding="windows-1252") as handle:
            for line in handle:
                if line.startswith("# SIGNALS:"):
                    in_block = True
                    continue
                if not in_block:
                    continue
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped == "#":
                    break
                if not line.startswith("#"):
                    continue
                content = line[2:]
                parts = [part.strip() for part in content.split(":")]
                if len(parts) >= 3:
                    signals[parts[0]] = parts[-1]
        return signals

    def test_value_elements_match_export_config(self):
        for idx, payload in self.stage_signals.items():
            signals = payload["signals"]
            for key in VALUE_KEYS:
                self.assertIn(key, signals, msg=f"Stage {idx} missing {key}")
            self.assertEqual(str(signals["project_name"]), BASE_CONFIG.project_name)
            self.assertEqual(str(signals["specimen_name"]), BASE_CONFIG.specimen_name)
            self.assertEqual(str(signals["exp_number"]), BASE_CONFIG.experiment_name)

    def test_stage_name_matches_signal_values(self):
        for idx, payload in self.stage_signals.items():
            signals = payload["signals"]
            is_ref = payload["is_ref"]
            if is_ref:
                continue
            for key in STRESS_KEYS:
                self.assertIn(key, signals, msg=f"Stage {idx} missing {key}")
            stage_components = self._extract_stage_components(payload["name"])
            self.assertGreaterEqual(len(stage_components), 3,
                                    msg=f"Stage name '{payload['name']}' does not contain three components")
            for component, key in zip(stage_components[:3], STRESS_KEYS):
                self.assertAlmostEqual(component, float(signals[key]), places=3,
                                       msg=f"Stage {idx} mismatch for {key}")

    def test_exported_nodemaps_contain_signal_metadata(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        export_config = replace(BASE_CONFIG, export_abs_path=temp_dir.name)
        exporter = AramisExporter(self.client, export_config)
        exporter.export_data_to_txt()
        nodemap_files = sorted(exporter.nm_subfolder_path.glob("*.txt"))
        self.assertTrue(nodemap_files, "No nodemap files were exported")
        for nodemap in nodemap_files:
            stage_idx = self._extract_stage_index_from_filename(nodemap)
            signals = self.stage_signals[stage_idx]["signals"]
            file_signals = self._read_signals_block(nodemap)
            self.assertTrue(file_signals, f"Missing # SIGNALS block in {nodemap.name}")
            for key in VALUE_KEYS:
                self.assertIn(key, file_signals, msg=f"{nodemap.name} missing {key} header entry")
                self.assertEqual(file_signals[key], str(signals[key]))
            for key in STRESS_KEYS:
                self.assertIn(key, file_signals, msg=f"{nodemap.name} missing {key} header entry")
                self.assertAlmostEqual(float(file_signals[key]), float(signals[key]), places=3)


if __name__ == "__main__":
    unittest.main(exit=False)

