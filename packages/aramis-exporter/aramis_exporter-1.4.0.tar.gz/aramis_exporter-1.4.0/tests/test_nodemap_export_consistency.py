"""Consistency tests verifying exported nodemaps against bundled reference data."""
import importlib
import tempfile
import unittest
from importlib.resources import as_file, files
from pathlib import Path

import numpy as np

from aramis_exporter.client import GOMClient
from aramis_exporter.exporter import AramisExporter, ExportConfig

DATA_DIR = files("aramis_exporter") / "test_data"
DATA_HEADER_PREFIX = "#       ID;"


class NodemapExportAlignmentTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.data_dir_cm = as_file(DATA_DIR)
		data_dir_path = Path(cls.data_dir_cm.__enter__())
		cls.test_project_path = data_dir_path / "aramis_projects" / "TestProjectPrepared.aramis"
		cls.reference_dir = data_dir_path / "nodemaps"

		cls.gom = importlib.import_module("gom")
		cls.temp_dir = tempfile.TemporaryDirectory()
		client = GOMClient(cls.gom)
		if client.project is not None:
			client.close_project()
		client.open_project(str(cls.test_project_path))
		cls.config = ExportConfig(
			project_name="TestProject",
			specimen_name="SP",
			experiment_name="SynLoads",
			export_abs_path=str(cls.temp_dir.name),
		)
		cls.exporter = AramisExporter(client, cls.config)
		cls.exporter.export_data_to_txt(export_connections=False)
		cls.reference_files = sorted(cls.reference_dir.glob("*.txt"), key=lambda path: path.name)
		cls.exported_files = sorted(cls.exporter.nm_subfolder_path.glob("*.txt"), key=lambda path: path.name)

	@classmethod
	def tearDownClass(cls):
		try:
			if getattr(cls, "exporter", None):
				client = cls.exporter.client
				if client.project is not None:
					client.close_project()
		finally:
			if getattr(cls, "temp_dir", None):
				cls.temp_dir.cleanup()
			if getattr(cls, "data_dir_cm", None):
				cls.data_dir_cm.__exit__(None, None, None)

	def test_exported_nodemaps_match_reference(self):
		self.assertTrue(self.reference_files, "reference nodemap files missing")
		self.assertTrue(self.exported_files, "export did not produce nodemaps")
		self.assertEqual(
			[path.name for path in self.reference_files],
			[path.name for path in self.exported_files],
			"Exported nodemap filenames differ from reference set",
		)
		for exported_path, reference_path in zip(self.exported_files, self.reference_files):
			exported_data = self._read_data_block(exported_path)
			reference_data = self._read_data_block(reference_path)
			self.assertEqual(
				exported_data.shape,
				reference_data.shape,
				msg=f"Data shape mismatch in {exported_path.name}",
			)
			np.testing.assert_allclose(
				exported_data,
				reference_data,
				rtol=1e-6,
				atol=1e-9,
				err_msg=f"Data values mismatch in {exported_path.name}",
			)

	@staticmethod
	def _read_data_block(path: Path):
		line_to_float = lambda line: list(map(float, line.split(";")))
		data_block = []
		header_found = False
		with path.open("r", encoding="windows-1252") as handle:
			for line in handle:
				if not header_found:
					if line.startswith(DATA_HEADER_PREFIX):
						header_found = True
						data_block.append(line.rstrip("\n"))
					continue
				data_block.append(line.rstrip("\n"))
		if not data_block:
			raise AssertionError(f"Header '{DATA_HEADER_PREFIX}' not found in {path}")
		data_split = [line_to_float(line) for line in data_block[1:]]
		data_block = np.array(data_split)
		return data_block


if __name__ == "__main__":
	unittest.main(exit=False)