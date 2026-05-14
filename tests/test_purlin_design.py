import base64
import math
import re
import unittest
import zlib
from pathlib import Path

from reportlab.platypus import CondPageBreak

from utils.pdf_report import _section_heading, _styles, _subheading, generate_purlin_pdf
from utils.purlin_calc import run_purlin_design
from utils.sections import (
    COLD_FORMED_C,
    COLD_FORMED_Z,
    COMMON_PURLIN_SECTION_TYPES,
    HOLLOW_BOX,
    ISA,
    ISMB,
)


def _decoded_pdf_page_streams(pdf_bytes: bytes) -> list[bytes]:
    """Return decoded ReportLab page content streams in page order."""
    pages_match = re.search(rb"/Count \d+ /Kids \[([^\]]+)\]", pdf_bytes)
    if not pages_match:
        return []

    page_ids = [int(match) for match in re.findall(rb"(\d+) 0 R", pages_match.group(1))]
    decoded_pages = []
    for page_id in page_ids:
        page_match = re.search(rf"{page_id} 0 obj(.*?)endobj".encode(), pdf_bytes, re.S)
        if not page_match:
            continue
        content_match = re.search(rb"/Contents (\d+) 0 R", page_match.group(1))
        if not content_match:
            decoded_pages.append(b"")
            continue

        content_id = int(content_match.group(1))
        content_match = re.search(
            rf"{content_id} 0 obj(.*?)endobj".encode(), pdf_bytes, re.S
        )
        if not content_match:
            decoded_pages.append(b"")
            continue

        stream = (
            content_match.group(1)
            .split(b"stream\n", 1)[1]
            .split(b"endstream", 1)[0]
            .strip()
        )
        decoded_pages.append(zlib.decompress(base64.a85decode(stream, adobe=True)))
    return decoded_pages


class PurlinDesignTests(unittest.TestCase):
    def setUp(self):
        self.input_data = {
            "span_m": 5.0,
            "spacing_m": 1.5,
            "roof_slope_deg": 10.0,
            "dead_load": 0.55,
            "live_load": 0.75,
            "wind_pressure": 0.70,
            "Cp_ext": -0.8,
            "Cp_int": 0.2,
            "fy": 250.0,
            "gm0": 1.10,
            "section_name": "ISMB 300",
            "section_props": ISMB["ISMB 300"],
        }

    def test_purlin_design_returns_real_design_values(self):
        result = run_purlin_design(self.input_data)

        self.assertEqual(result["section_name"], "ISMB 300")
        self.assertEqual(result["overall_status"], "SAFE")
        self.assertGreater(result["Mz_kNm"], 0.0)
        self.assertGreater(result["Mdz_kNm"], result["Mz_kNm"])
        self.assertLess(result["biaxial_ratio"], 1.0)
        self.assertTrue(result["biaxial_ok"])
        self.assertTrue(result["shear_ok"])
        self.assertTrue(result["defl_ok"])
        self.assertTrue(math.isclose(result["sw_kNm"], 44.2 * 9.81 / 1000.0))

    def test_purlin_design_includes_lap_splice_check_for_cold_formed_only(self):
        data = dict(self.input_data)
        data.update(
            {
                "span_m": 3.0,
                "section_name": "CFLC 250x75x25x2.5",
                "section_props": COLD_FORMED_C["CFLC 250x75x25x2.5"],
                "lap_length_m": 0.75,
                "lap_bolt_dia_mm": 16.0,
                "lap_bolt_rows": 2,
                "lap_bolts_per_row": 2,
                "lap_bolt_grade_fub": 400.0,
                "lap_plate_fu": 410.0,
            }
        )

        result = run_purlin_design(data)
        lap = result["lap_design"]

        self.assertTrue(lap["applicable"])
        self.assertIn("Cold-formed", lap["method"])
        self.assertEqual(lap["bolt_count"], 4)
        self.assertAlmostEqual(lap["provided_lap_mm"], 750.0)
        self.assertAlmostEqual(lap["recommended_lap_mm"], 600.0)
        self.assertTrue(lap["lap_length_ok"])
        self.assertGreater(lap["support_reaction_kN"], result["Vz_kN"])
        self.assertGreater(lap["group_capacity_kN"], lap["support_reaction_kN"])
        self.assertTrue(lap["overall_ok"])

    def test_purlin_lap_length_can_govern_cold_formed_overall_status(self):
        data = dict(self.input_data)
        data.update(
            {
                "span_m": 3.0,
                "section_name": "CFLC 250x75x25x2.5",
                "section_props": COLD_FORMED_C["CFLC 250x75x25x2.5"],
                "lap_length_m": 0.25,
            }
        )

        result = run_purlin_design(data)
        lap = result["lap_design"]

        self.assertTrue(lap["applicable"])
        self.assertFalse(lap["lap_length_ok"])
        self.assertFalse(lap["overall_ok"])
        self.assertEqual(result["overall_status"], "UNSAFE")

    def test_hot_rolled_sections_do_not_allow_nested_lap_design(self):
        data = dict(self.input_data)
        data.update({"lap_length_m": 0.25})

        result = run_purlin_design(data)
        lap = result["lap_design"]

        self.assertFalse(lap["applicable"])
        self.assertTrue(lap["overall_ok"])
        self.assertEqual(result["overall_status"], "SAFE")
        self.assertIn("cold-formed lipped C/Z", lap["note"])

    def test_purlin_design_derives_radius_and_stability_checks(self):
        result = run_purlin_design(self.input_data)

        self.assertAlmostEqual(result["rxx_cm"], math.sqrt(8603.0 / 56.2))
        self.assertAlmostEqual(result["ryy_cm"], math.sqrt(453.0 / 56.2))
        self.assertTrue(result["stability_checks"]["wind_uplift_present"])
        self.assertTrue(result["stability_checks"]["overall_ok"])
        self.assertGreater(result["stability_checks"]["uplift_moment_kNm"], 0.0)

    def test_self_weight_and_restraint_inputs_can_govern_purlin_design(self):
        data = dict(self.input_data)
        data.update(
            {
                "dead_load_excludes_self_weight": False,
                "top_flange_restrained": False,
                "bottom_flange_restrained": False,
            }
        )

        result = run_purlin_design(data)

        self.assertEqual(result["sw_added_kNm"], 0.0)
        self.assertLess(
            result["w_dl_total"],
            self.input_data["dead_load"] * self.input_data["spacing_m"]
            + result["sw_kNm"],
        )
        self.assertFalse(result["stability_checks"]["overall_ok"])
        self.assertEqual(result["overall_status"], "UNSAFE")

    def test_common_purlin_section_guidance_lists_is_based_families(self):
        designations = {item["designation"] for item in COMMON_PURLIN_SECTION_TYPES}
        section_types = {item["type"] for item in COMMON_PURLIN_SECTION_TYPES}
        shapes = {item["shape"] for item in COMMON_PURLIN_SECTION_TYPES}

        self.assertIn("ISMC / ISLC", designations)
        self.assertIn("ISMB / ISLB", designations)
        self.assertIn("ISA", designations)
        self.assertIn("C / lipped C", designations)
        self.assertIn("Z / lipped Z", designations)
        self.assertIn("IS 4923 tubular sections", designations)
        self.assertIn("Cold-formed Z-sections", section_types)
        self.assertIn("C-channel / U-channel", shapes)
        self.assertIn("I-shape / beam profile", shapes)
        self.assertIn("L-shape / double-angle", shapes)
        self.assertIn("RHS / SHS / box profile", shapes)

    def test_added_purlin_section_databases_run_design_calculations(self):
        section_sets = {
            "ISA 100x100x10": ISA["ISA 100x100x10"],
            "CFLC 250x75x25x2.5": COLD_FORMED_C["CFLC 250x75x25x2.5"],
            "CFLZ 250x75x25x2.5": COLD_FORMED_Z["CFLZ 250x75x25x2.5"],
            "RHS 200x100x5.0": HOLLOW_BOX["RHS 200x100x5.0"],
        }

        for section_name, section_props in section_sets.items():
            with self.subTest(section_name=section_name):
                data = dict(self.input_data)
                data.update(
                    {
                        "span_m": 3.0,
                        "section_name": section_name,
                        "section_props": section_props,
                    }
                )

                result = run_purlin_design(data)

                self.assertEqual(result["section_name"], section_name)
                self.assertGreater(result["Mdz_kNm"], 0.0)
                self.assertGreater(result["Mdy_kNm"], 0.0)
                self.assertGreater(result["Vd_kN"], 0.0)
                self.assertTrue(math.isfinite(result["biaxial_ratio"]))
                self.assertTrue(math.isfinite(result["defl_ratio"]))
                self.assertNotEqual(result["section_class"]["overall"], "Slender")
                if section_name.startswith(("CFLC", "CFLZ")):
                    cold_checks = result["cold_formed_checks"]
                    self.assertIn("effective-width", result["design_standard"])
                    self.assertGreater(cold_checks["area_eff_ratio"], 0.0)
                    self.assertLessEqual(cold_checks["area_eff_ratio"], 1.0)
                    self.assertGreater(cold_checks["Zxx_eff"], 0.0)
                    self.assertGreater(cold_checks["Vd_shear_kN"], 0.0)
                    self.assertIn("web_crippling_ok", cold_checks["checks"])
                    self.assertIn("distortional_ok", cold_checks["checks"])
                else:
                    self.assertIn("gross-section", result["design_standard"])

    def test_design_code_selection_controls_cold_formed_checks(self):
        data = dict(self.input_data)
        data.update(
            {
                "span_m": 3.0,
                "section_name": "CFLC 250x75x25x2.5",
                "section_props": COLD_FORMED_C["CFLC 250x75x25x2.5"],
                "design_code": "IS 800:2007",
            }
        )

        is800_result = run_purlin_design(data)
        self.assertEqual(is800_result["design_code"], "IS 800:2007")
        self.assertIn("gross-section", is800_result["design_standard"])
        self.assertEqual(is800_result["cold_formed_checks"], {})

        data["design_code"] = "IS 801:1975"
        is801_result = run_purlin_design(data)
        self.assertEqual(is801_result["design_code"], "IS 801:1975")
        self.assertIn("effective-width", is801_result["design_standard"])
        self.assertIn("overall_ok", is801_result["cold_formed_checks"]["checks"])

    def test_purlin_page_refreshes_existing_result_when_inputs_change(self):
        page_source = Path("pages/1_Purlin_Design.py").read_text()

        self.assertIn(
            'st.session_state.get("purlin_input") != current_input', page_source
        )
        self.assertIn(
            "_store_current_purlin_design(show_refresh_notice=True)", page_source
        )
        self.assertIn(
            "pdf_bytes = generate_purlin_pdf(r, project=project_name)", page_source
        )

    def test_pdf_topic_headers_request_page_break_space(self):
        styles = _styles()
        section_flowables = _section_heading("TEST SECTION", styles)
        subheading_flowables = _subheading("Test Subheading", styles)

        self.assertIsInstance(section_flowables[0], CondPageBreak)
        self.assertIsInstance(subheading_flowables[0], CondPageBreak)
        self.assertTrue(styles["h1"].keepWithNext)
        self.assertTrue(styles["h2"].keepWithNext)

    def test_pdf_report_generation_uses_calculation_output(self):
        result = run_purlin_design(self.input_data)
        pdf_bytes = generate_purlin_pdf(result, project="Unit Test Project")

        decoded_pages = _decoded_pdf_page_streams(pdf_bytes)

        self.assertGreater(len(pdf_bytes), 5000)
        self.assertEqual(pdf_bytes[:4], b"%PDF")
        self.assertTrue(any(b"12.37" in page for page in decoded_pages))
        self.assertTrue(any(b"Self-weight note" in page for page in decoded_pages))
        self.assertTrue(any(b"LTB" in page for page in decoded_pages))

    def test_purlin_pdf_does_not_end_with_blank_footer_page(self):
        result = run_purlin_design(self.input_data)
        pdf_bytes = generate_purlin_pdf(result, project="Unit Test Project")
        decoded_pages = _decoded_pdf_page_streams(pdf_bytes)

        self.assertGreaterEqual(len(decoded_pages), 1)
        self.assertIn(b"REFERENCES", decoded_pages[-1])
        self.assertGreater(decoded_pages[-1].count(b" Tj"), 20)


if __name__ == "__main__":
    unittest.main()
