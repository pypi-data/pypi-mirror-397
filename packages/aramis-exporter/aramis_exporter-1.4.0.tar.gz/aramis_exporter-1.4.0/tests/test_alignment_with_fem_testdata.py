"""Validates facet-based average strains against FEM summary files."""
import importlib
import json
import unittest
from importlib.resources import files
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from aramis_exporter.client import GOMClient

DATA_DIR = files("aramis_exporter") / "test_data"
TEST_PROJECT = DATA_DIR / "aramis_projects" / "TestProjectPrepared.aramis"
FEM_RESULTS_DIR = DATA_DIR / "fem_results"
AVG_EPS_KEYS = ("avg_epto_xx", "avg_epto_yy", "avg_epto_xy")
DISP_KEY = "sim_disp"
DISP_POST_KEYS = ("Top Center", "Bottom Center", "Left Center", "Right Center")


class FemSummaryAlignmentTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.gom = importlib.import_module("gom")
		cls.client = GOMClient(cls.gom)
		if cls.client.project is not None:
			cls.client.close_project()
		cls.client.open_project(str(TEST_PROJECT))
		cls.client.initialize()
		cls.stage_index_map = cls._build_stage_index_map()
		cls.summary_files = cls._load_summary_payloads()
		cls._avg_cache: Dict[int, Dict[str, float]] = {}

	@classmethod
	def tearDownClass(cls):
		cls.client.close_project()

	@classmethod
	def _build_stage_index_map(cls) -> Dict[str, int]:
		stage_map: Dict[str, int] = {}
		num_stages = cls.client.get_num_stages()
		ref_stage = cls.client.get_ref_stage_index()
		for stage_idx in range(num_stages):
			if stage_idx == ref_stage:
				continue
			stage_name = cls.client.project.stages[stage_idx].get("name")
			stage_name = "_".join(stage_name.split("_")[:3])
			stage_map[stage_name] = stage_idx
		if not stage_map:
			raise AssertionError("No stages discovered in project")
		return stage_map

	@classmethod
	def _load_summary_payloads(cls) -> Dict[str, Tuple[Path, Dict[str, float]]]:
		payloads: Dict[str, Tuple[Path, Dict[str, float]]] = {}
		for file_path in FEM_RESULTS_DIR.iterdir():
			if file_path.name.endswith("_summary.json"):
				key = file_path.name.replace("_summary.json", "")
				with file_path.open("r", encoding="utf-8") as handle:
					payloads[key] = (file_path, json.load(handle))
		if not payloads:
			raise AssertionError("No FEM summary files found")
		return payloads

	@classmethod
	def _compute_strain_averages(cls, stage_idx: int) -> Dict[str, float]:
		if stage_idx not in cls._avg_cache:
			cls.client.show_stage(stage_idx)
			facet_data = cls.client.get_current_stage_results()
			cls._avg_cache[stage_idx] = {
				"avg_epto_xx": float(np.nanmean(facet_data.eps_x)),
				"avg_epto_yy": float(np.nanmean(facet_data.eps_y)),
				"avg_epto_xy": float(np.nanmean(facet_data.eps_xy)),
			}
		return cls._avg_cache[stage_idx]

	@classmethod
	def _compute_disp_at_boundary_mids(cls, stage_idx: int, limit_mm: float = 1.0) -> Dict[str, Tuple]:
		cls.client.show_stage(stage_idx)
		facet_data = cls.client.get_current_stage_results()
		left, right, bottom, top = cls._compute_facet_boundaries_mids(stage_idx, atol_mm=limit_mm)
		disp_left = (np.nanmean(facet_data.disp_x[left]), np.nanmean(facet_data.disp_y[left]))
		disp_right = (np.nanmean(facet_data.disp_x[right]), np.nanmean(facet_data.disp_y[right]))
		disp_bottom = (np.nanmean(facet_data.disp_x[bottom]), np.nanmean(facet_data.disp_y[bottom]))
		disp_top = (np.nanmean(facet_data.disp_x[top]), np.nanmean(facet_data.disp_y[top]))
		return {
			"disp_left": disp_left,
			"disp_right": disp_right,
			"disp_bottom": disp_bottom,
			"disp_top": disp_top,
		}

	@classmethod
	def _compute_facet_boundaries_mids(cls, stage_idx, atol_mm=0.5):
		"""Returns a mask of the boundaries"""
		facet_data = cls.client.get_current_stage_results()
		coords = facet_data.facet_coordinates
		x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
		y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
		left_center = (x_min - atol_mm, x_min + atol_mm, (y_min + y_max) / 2 - atol_mm, (y_min + y_max) / 2 + atol_mm)
		right_center = (x_max - atol_mm, x_max + atol_mm, (y_min + y_max) / 2 - atol_mm, (y_min + y_max) / 2 + atol_mm)
		bottom_center = ((x_min + x_max) / 2 - atol_mm, (x_min + x_max) / 2 + atol_mm, y_min - atol_mm, y_min + atol_mm)
		top_center = ((x_min + x_max) / 2 - atol_mm, (x_min + x_max) / 2 + atol_mm, y_max - atol_mm, y_max + atol_mm)
		left = np.where(
			(coords[:, 0] >= left_center[0]) & (coords[:, 0] <= left_center[1]) &
			(coords[:, 1] >= left_center[2]) & (coords[:, 1] <= left_center[3])
		)[0]
		right = np.where(
			(coords[:, 0] >= right_center[0]) & (coords[:, 0] <= right_center[1]) &
			(coords[:, 1] >= right_center[2]) & (coords[:, 1] <= right_center[3])
		)[0]
		bottom = np.where(
			(coords[:, 0] >= bottom_center[0]) & (coords[:, 0] <= bottom_center[1]) &
			(coords[:, 1] >= bottom_center[2]) & (coords[:, 1] <= bottom_center[3])
		)[0]
		top = np.where(
			(coords[:, 0] >= top_center[0]) & (coords[:, 0] <= top_center[1]) &
			(coords[:, 1] >= top_center[2]) & (coords[:, 1] <= top_center[3])
		)[0]
		return left, right, bottom, top

	def test_facet_boundary_displacements_matches_fem_summary(self):
		for stage_key, (file_path, summary) in self.summary_files.items():
			self.assertIn(stage_key, self.stage_index_map, msg=f"No stage matches {file_path.name}")
			# exclude stages with shear boundary conditions for now -> issue with rmbc
			if float(stage_key.split("_")[-1]):
				continue
			stage_idx = self.stage_index_map[stage_key]
			facet_disps = self._compute_disp_at_boundary_mids(stage_idx)
			disps = summary.get(DISP_KEY, {})
			self.assertIsInstance(disps, dict, msg=f"{file_path.name} missing {DISP_KEY} dict")
			summary = {f"disp_{key.split()[0].lower()}": value for key, value in disps.items() if key in DISP_POST_KEYS}
			for key in summary:
				self.assertIn(key, facet_disps, msg=f"{file_path.name} missing {key}")
				disp_x_facet, disp_y_facet = facet_disps[key]
				disp_x_fem, disp_y_fem = eval(summary[key])[1:3]
				self.assertAlmostEqual(disp_x_facet,disp_x_fem, delta=0.02,
												msg=f"Mismatch for {key} X at stage '{stage_key}'")
				self.assertAlmostEqual(disp_y_facet, disp_y_fem, delta=0.02,
												msg=f"Mismatch for {key} Y at stage '{stage_key}'")

	def test_facet_average_strains_matches_fem_summary(self):
		for stage_key, (file_path, summary) in self.summary_files.items():
			self.assertIn(stage_key, self.stage_index_map, msg=f"No stage matches {file_path.name}")
			# exclude stages with shear boundary conditions for now -> issue with rmbc
			if float(stage_key.split("_")[-1]):
				continue
			stage_idx = self.stage_index_map[stage_key]
			facet_avgs = self._compute_strain_averages(stage_idx)

			for key in AVG_EPS_KEYS:
				self.assertIn(key, summary, msg=f"{file_path.name} missing {key}")
				self.assertAlmostEqual(facet_avgs[key], float(summary[key]) * 100, places=2,
												msg=f"Mismatch for {key} at stage '{stage_key}'")


class FemSummaryAlignmentWoRbmcTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.gom = importlib.import_module("gom")
		cls.client = GOMClient(cls.gom)
		if cls.client.project is not None:
			cls.client.close_project()
		cls.client.open_project(str(TEST_PROJECT))
		cls.client.initialize(set_rbmc_active=False)
		cls.stage_index_map = cls._build_stage_index_map()
		cls.summary_files = cls._load_summary_payloads()
		cls._avg_cache: Dict[int, Dict[str, float]] = {}

	@classmethod
	def tearDownClass(cls):
		cls.client.close_project()

	@classmethod
	def _build_stage_index_map(cls) -> Dict[str, int]:
		stage_map: Dict[str, int] = {}
		num_stages = cls.client.get_num_stages()
		ref_stage = cls.client.get_ref_stage_index()
		for stage_idx in range(num_stages):
			if stage_idx == ref_stage:
				continue
			stage_name = cls.client.project.stages[stage_idx].get("name")
			stage_name = "_".join(stage_name.split("_")[:3])
			stage_map[stage_name] = stage_idx
		if not stage_map:
			raise AssertionError("No stages discovered in project")
		return stage_map

	@classmethod
	def _load_summary_payloads(cls) -> Dict[str, Tuple[Path, Dict[str, float]]]:
		payloads: Dict[str, Tuple[Path, Dict[str, float]]] = {}
		for file_path in FEM_RESULTS_DIR.iterdir():
			if file_path.name.endswith("_summary.json"):
				key = file_path.name.replace("_summary.json", "")
				with file_path.open("r", encoding="utf-8") as handle:
					payloads[key] = (file_path, json.load(handle))
		if not payloads:
			raise AssertionError("No FEM summary files found")
		return payloads

	@classmethod
	def _compute_strain_averages(cls, stage_idx: int) -> Dict[str, float]:
		if stage_idx not in cls._avg_cache:
			cls.client.show_stage(stage_idx)
			facet_data = cls.client.get_current_stage_results()
			cls._avg_cache[stage_idx] = {
				"avg_epto_xx": float(np.nanmean(facet_data.eps_x)),
				"avg_epto_yy": float(np.nanmean(facet_data.eps_y)),
				"avg_epto_xy": float(np.nanmean(facet_data.eps_xy)),
			}
		return cls._avg_cache[stage_idx]

	@classmethod
	def _compute_disp_at_boundary_mids(cls, stage_idx: int, limit_mm: float = 1.0) -> Dict[str, Tuple]:
		cls.client.show_stage(stage_idx)
		facet_data = cls.client.get_current_stage_results()
		left, right, bottom, top = cls._compute_facet_boundaries_mids(stage_idx, atol_mm=limit_mm)
		disp_left = (np.nanmean(facet_data.disp_x[left]), np.nanmean(facet_data.disp_y[left]))
		disp_right = (np.nanmean(facet_data.disp_x[right]), np.nanmean(facet_data.disp_y[right]))
		disp_bottom = (np.nanmean(facet_data.disp_x[bottom]), np.nanmean(facet_data.disp_y[bottom]))
		disp_top = (np.nanmean(facet_data.disp_x[top]), np.nanmean(facet_data.disp_y[top]))
		return {
			"disp_left": disp_left,
			"disp_right": disp_right,
			"disp_bottom": disp_bottom,
			"disp_top": disp_top,
		}

	@classmethod
	def _compute_facet_boundaries_mids(cls, stage_idx, atol_mm=0.5):
		"""Returns a mask of the boundaries"""
		facet_data = cls.client.get_current_stage_results()
		coords = facet_data.facet_coordinates
		x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
		y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
		left_center = (x_min - atol_mm, x_min + atol_mm, (y_min + y_max) / 2 - atol_mm, (y_min + y_max) / 2 + atol_mm)
		right_center = (x_max - atol_mm, x_max + atol_mm, (y_min + y_max) / 2 - atol_mm, (y_min + y_max) / 2 + atol_mm)
		bottom_center = ((x_min + x_max) / 2 - atol_mm, (x_min + x_max) / 2 + atol_mm, y_min - atol_mm, y_min + atol_mm)
		top_center = ((x_min + x_max) / 2 - atol_mm, (x_min + x_max) / 2 + atol_mm, y_max - atol_mm, y_max + atol_mm)
		left = np.where(
			(coords[:, 0] >= left_center[0]) & (coords[:, 0] <= left_center[1]) &
			(coords[:, 1] >= left_center[2]) & (coords[:, 1] <= left_center[3])
		)[0]
		right = np.where(
			(coords[:, 0] >= right_center[0]) & (coords[:, 0] <= right_center[1]) &
			(coords[:, 1] >= right_center[2]) & (coords[:, 1] <= right_center[3])
		)[0]
		bottom = np.where(
			(coords[:, 0] >= bottom_center[0]) & (coords[:, 0] <= bottom_center[1]) &
			(coords[:, 1] >= bottom_center[2]) & (coords[:, 1] <= bottom_center[3])
		)[0]
		top = np.where(
			(coords[:, 0] >= top_center[0]) & (coords[:, 0] <= top_center[1]) &
			(coords[:, 1] >= top_center[2]) & (coords[:, 1] <= top_center[3])
		)[0]
		return left, right, bottom, top

	def test_facet_boundary_displacements_matches_fem_summary(self):
		for stage_key, (file_path, summary) in self.summary_files.items():
			self.assertIn(stage_key, self.stage_index_map, msg=f"No stage matches {file_path.name}")
			stage_idx = self.stage_index_map[stage_key]
			facet_disps = self._compute_disp_at_boundary_mids(stage_idx)
			disps = summary.get(DISP_KEY, {})
			self.assertIsInstance(disps, dict, msg=f"{file_path.name} missing {DISP_KEY} dict")
			summary = {f"disp_{key.split()[0].lower()}": value for key, value in disps.items() if key in DISP_POST_KEYS}
			for key in summary:
				self.assertIn(key, facet_disps, msg=f"{file_path.name} missing {key}")
				disp_x_facet, disp_y_facet = facet_disps[key]
				disp_x_fem, disp_y_fem = eval(summary[key])[1:3]
				self.assertAlmostEqual(disp_x_facet,disp_x_fem, delta=0.02,
												msg=f"Mismatch for {key} X at stage '{stage_key}'")
				self.assertAlmostEqual(disp_y_facet, disp_y_fem, delta=0.02,
												msg=f"Mismatch for {key} Y at stage '{stage_key}'")

	def test_facet_average_strains_matches_fem_summary(self):
		for stage_key, (file_path, summary) in self.summary_files.items():
			self.assertIn(stage_key, self.stage_index_map, msg=f"No stage matches {file_path.name}")
			# exclude stages with shear boundary conditions for now -> issue with rmbc
			if float(stage_key.split("_")[-1]):
				continue
			stage_idx = self.stage_index_map[stage_key]
			facet_avgs = self._compute_strain_averages(stage_idx)

			for key in AVG_EPS_KEYS:
				self.assertIn(key, summary, msg=f"{file_path.name} missing {key}")
				self.assertAlmostEqual(facet_avgs[key], float(summary[key]) * 100, places=2,
												msg=f"Mismatch for {key} at stage '{stage_key}'")


if __name__ == "__main__":
	unittest.main(exit=False)
