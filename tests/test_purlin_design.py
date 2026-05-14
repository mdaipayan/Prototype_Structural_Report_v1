import math
import unittest

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

        self.assertGreater(len(pdf_bytes), 5000)
        self.assertEqual(pdf_bytes[:4], b"%PDF")


if __name__ == "__main__":
    unittest.main()
