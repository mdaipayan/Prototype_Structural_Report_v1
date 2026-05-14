"""Purlin design calculations for the Streamlit UI and PDF report.

The module keeps the engineering arithmetic in one place so that the web page
and the generated report always use the same values.  Units are noted at each
conversion boundary because most section properties are stored in traditional
steel-table units (cm², cm³, cm⁴) while IS 800 equations use N-mm units.
"""

from __future__ import annotations

import math
from typing import Any

SECTION_CLASS_ORDER = {"Plastic": 1, "Compact": 2, "Semi-compact": 3, "Slender": 4}


def _as_float(value: Any, default: float = 0.0) -> float:
    """Return a numeric value without letting bad UI/session data crash a run."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _classify_ratio(ratio: float, limits: list[float]) -> str:
    if ratio <= limits[0]:
        return "Plastic"
    if ratio <= limits[1]:
        return "Compact"
    if ratio <= limits[2]:
        return "Semi-compact"
    return "Slender"


def _section_classification(sp: dict[str, Any], fy: float) -> dict[str, Any]:
    """Classify flanges/webs using IS 800:2007 Table 2 style limits.

    Non-I rolled/cold-formed/tubular purlin databases can provide a conservative
    gross-section override so the shared design workflow still returns finite
    capacities while the UI/PDF exposes final-design notes for specialist checks.
    """
    epsilon = math.sqrt(250.0 / fy) if fy > 0 else 1.0

    bf = _as_float(sp.get("bf"))
    tw = _as_float(sp.get("tw"), 1.0)
    tf = _as_float(sp.get("tf"), 1.0)
    h = _as_float(sp.get("h"))

    b_tf = max((bf - tw) / (2.0 * tf), 0.0) if tf else math.inf
    d_tw = max((h - 2.0 * tf) / tw, 0.0) if tw else math.inf

    flange_limits = [9.4 * epsilon, 13.6 * epsilon, 15.7 * epsilon]
    web_limits = [84.0 * epsilon, 105.0 * epsilon, 126.0 * epsilon]

    flange_class = _classify_ratio(b_tf, flange_limits)
    web_class = _classify_ratio(d_tw, web_limits)
    overall = max(
        [flange_class, web_class], key=lambda label: SECTION_CLASS_ORDER[label]
    )

    override = sp.get("section_class_override")
    if override in SECTION_CLASS_ORDER:
        overall = override

    return {
        "name": overall,
        "overall": overall,
        "class_type": SECTION_CLASS_ORDER[overall],
        "epsilon": epsilon,
        "b_tf": b_tf,
        "d_tw": d_tw,
        "flange_class": flange_class,
        "web_class": web_class,
        "limits": {"flange": flange_limits, "web": web_limits},
        "override": override,
    }


COLD_FORMED_FAMILIES = {"Cold-formed C-sections", "Cold-formed Z-sections"}


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def _effective_plate(
    width_mm: float, thickness_mm: float, fy: float, k: float
) -> dict[str, float]:
    """Return Winter-style effective-width data for a cold-formed plate element."""
    E = 2.0e5
    nu = 0.3
    width = max(width_mm, 0.0)
    thickness = max(thickness_mm, 0.0)
    if width <= 0 or thickness <= 0 or fy <= 0 or k <= 0:
        return {
            "flat_width": width,
            "ratio": math.inf,
            "fcr": 0.0,
            "lambda": math.inf,
            "rho": 0.0,
            "effective_width": 0.0,
        }

    ratio = width / thickness
    fcr = k * math.pi**2 * E / (12.0 * (1.0 - nu**2) * ratio**2)
    slenderness = math.sqrt(fy / fcr) if fcr > 0 else math.inf
    rho = 1.0 if slenderness <= 0.673 else (1.0 - 0.22 / slenderness) / slenderness
    rho = _clamp(rho, 0.0, 1.0)
    return {
        "flat_width": width,
        "ratio": ratio,
        "fcr": fcr,
        "lambda": slenderness,
        "rho": rho,
        "effective_width": rho * width,
    }


def _cold_formed_design_checks(
    sp: dict[str, Any],
    fy: float,
    gm0: float,
    Mz_kNm: float,
    My_kNm: float,
    Vz_kN: float,
    service_w: float,
    L_mm: float,
) -> dict[str, Any]:
    """Cold-formed lipped C/Z effective-width and stability checks.

    The implementation uses gross flat-element geometry from the local database,
    Winter-style effective widths for local buckling, web shear buckling stress,
    lip geometry limits for distortional stability screening, web-crippling
    reaction capacity at end supports, and effective inertia for serviceability.
    """
    h = _as_float(sp.get("h"))
    b = _as_float(sp.get("bf"))
    lip = _as_float(sp.get("lip"))
    t = _as_float(sp.get("tw"), _as_float(sp.get("tf"), 0.0))
    area_gross_mm2 = _as_float(sp.get("Area")) * 100.0
    av_mm2 = _as_float(sp.get("Av"), h * t)

    web = _effective_plate(max(h - 2.0 * t, 0.0), t, fy, 4.0)
    flange = _effective_plate(max(b - t, 0.0), t, fy, 4.0)
    lip_plate = _effective_plate(lip, t, fy, 0.43)

    area_eff_mm2 = (
        web["effective_width"] * t
        + 2.0 * flange["effective_width"] * t
        + 2.0 * lip_plate["effective_width"] * t
    )
    area_eff_ratio = _clamp(_safe_ratio(area_eff_mm2, area_gross_mm2), 0.20, 1.0)

    # Lipped C/Z purlins are thin-walled; use effective elastic section modulus.
    zxx_eff = _as_float(sp.get("Zxx")) * area_eff_ratio
    zyy_eff = _as_float(sp.get("Zyy")) * area_eff_ratio
    ixx_eff = _as_float(sp.get("Ixx")) * max(area_eff_ratio, 0.25)

    Mdz_eff = zxx_eff * fy / (gm0 * 1000.0) if gm0 else 0.0
    Mdy_eff = zyy_eff * fy / (gm0 * 1000.0) if gm0 else 0.0
    bending_ratio = _safe_ratio(My_kNm, Mdy_eff) + _safe_ratio(Mz_kNm, Mdz_eff)

    web_ratio = _safe_ratio(max(h - 2.0 * t, 0.0), t)
    shear_k = 5.34
    tau_cr = (
        shear_k * math.pi**2 * 2.0e5 / (12.0 * (1.0 - 0.3**2) * web_ratio**2)
        if math.isfinite(web_ratio) and web_ratio > 0
        else 0.0
    )
    tau_design = min(0.60 * fy, tau_cr)
    Vd_shear = av_mm2 * tau_design / (gm0 * 1000.0) if gm0 else 0.0
    shear_ratio = _safe_ratio(Vz_kN, Vd_shear)

    bearing_length = max(50.0, min(b, 100.0))
    web_crippling_capacity = (
        t**2
        * fy
        * (10.0 + 1.5 * bearing_length / max(t, 1.0))
        * (1.0 + 0.002 * web_ratio)
        / (gm0 * 1000.0)
        if gm0
        else 0.0
    )
    web_crippling_ratio = _safe_ratio(Vz_kN, web_crippling_capacity)

    flange_ratio = _safe_ratio(max(b - t, 0.0), t)
    lip_ratio = _safe_ratio(lip, t)
    lip_to_flange = _safe_ratio(lip, b)
    slenderness_ok = web_ratio <= 200.0 and flange_ratio <= 60.0 and lip_ratio <= 30.0
    distortional_ok = 0.20 <= lip_to_flange <= 0.60 and lip_ratio <= 30.0

    E = 2.0e5
    ixx_eff_mm4 = ixx_eff * 1.0e4
    delta_eff = (
        5.0 * service_w * L_mm**4 / (384.0 * E * ixx_eff_mm4)
        if ixx_eff_mm4 > 0
        else math.inf
    )

    checks = {
        "local_buckling_ok": area_eff_ratio >= 0.35 and slenderness_ok,
        "distortional_ok": distortional_ok,
        "effective_width_bending_ok": bending_ratio <= 1.0,
        "shear_buckling_ok": shear_ratio <= 1.0,
        "web_crippling_ok": web_crippling_ratio <= 1.0,
        "serviceability_ok": math.isfinite(delta_eff),
    }
    checks["overall_ok"] = all(checks.values())

    return {
        "is_cold_formed": True,
        "method": "IS 801 / effective-width cold-formed member checks",
        "web": web,
        "flange": flange,
        "lip": lip_plate,
        "area_gross_mm2": area_gross_mm2,
        "area_eff_mm2": area_eff_mm2,
        "area_eff_ratio": area_eff_ratio,
        "Zxx_eff": zxx_eff,
        "Zyy_eff": zyy_eff,
        "Ixx_eff": ixx_eff,
        "Mdz_eff_kNm": Mdz_eff,
        "Mdy_eff_kNm": Mdy_eff,
        "bending_ratio": bending_ratio,
        "tau_cr_MPa": tau_cr,
        "tau_design_MPa": tau_design,
        "Vd_shear_kN": Vd_shear,
        "shear_ratio": shear_ratio,
        "bearing_length_mm": bearing_length,
        "web_crippling_capacity_kN": web_crippling_capacity,
        "web_crippling_ratio": web_crippling_ratio,
        "web_slenderness": web_ratio,
        "flange_slenderness": flange_ratio,
        "lip_slenderness": lip_ratio,
        "lip_to_flange": lip_to_flange,
        "delta_eff_mm": delta_eff,
        "checks": checks,
    }


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return math.inf if numerator > 0 else 0.0
    return numerator / denominator


def _bolt_lap_design(
    sp: dict[str, Any],
    Vz_kN: float,
    Vy_kN: float,
    span_m: float,
    lap_length_m: float,
    bolt_dia_mm: float,
    bolt_rows: float,
    bolts_per_row: float,
    bolt_grade_fub: float,
    plate_fu: float,
) -> dict[str, Any]:
    """Return a practical purlin lap/splice connection design check.

    The lap is checked as a bolted purlin-to-purlin connection at a support.
    The design action is conservatively taken as the resultant support reaction
    from the governing purlin load case, shared equally by the provided bolts.
    Bolt shear and bearing capacities follow the IS 800:2007 bearing-bolt format
    using conservative default edge/pitch detailing when the UI does not expose
    those dimensions.
    """
    span_mm = max(span_m * 1000.0, 0.0)
    provided_lap_mm = max(lap_length_m * 1000.0, 0.0)
    recommended_lap_mm = max(0.10 * span_mm, 600.0)
    lap_length_ok = provided_lap_mm >= recommended_lap_mm

    d = max(bolt_dia_mm, 0.0)
    hole_dia = d + 2.0 if d <= 24.0 else d + 3.0
    rows = max(int(round(bolt_rows)), 0)
    per_row = max(int(round(bolts_per_row)), 0)
    bolt_count = rows * per_row
    gamma_mb = 1.25
    threads_area = 0.78 * math.pi * d**2 / 4.0
    shank_area = math.pi * d**2 / 4.0
    shear_capacity_kN = (
        bolt_grade_fub * threads_area / (math.sqrt(3.0) * gamma_mb * 1000.0)
        if d > 0 and bolt_grade_fub > 0
        else 0.0
    )

    t = _as_float(sp.get("tw"), _as_float(sp.get("tf"), 0.0))
    edge_mm = 1.7 * hole_dia
    pitch_mm = 3.0 * d
    kb_terms = [
        _safe_ratio(edge_mm, 3.0 * hole_dia),
        _safe_ratio(pitch_mm, 3.0 * hole_dia) - 0.25,
        _safe_ratio(bolt_grade_fub, plate_fu),
        1.0,
    ]
    kb = _clamp(min(kb_terms), 0.0, 1.0)
    bearing_capacity_kN = (
        2.5 * kb * d * t * plate_fu / (gamma_mb * 1000.0)
        if d > 0 and t > 0 and plate_fu > 0
        else 0.0
    )
    bolt_capacity_kN = min(shear_capacity_kN, bearing_capacity_kN)

    support_reaction_kN = math.hypot(Vz_kN, Vy_kN)
    demand_per_bolt_kN = _safe_ratio(support_reaction_kN, bolt_count)
    group_capacity_kN = bolt_count * bolt_capacity_kN
    bolt_utilisation = _safe_ratio(support_reaction_kN, group_capacity_kN)
    bolts_ok = bolt_utilisation <= 1.0

    end_distance_ok = edge_mm >= 1.5 * hole_dia
    pitch_ok = pitch_mm >= 2.5 * d if d > 0 else False
    detailing_ok = end_distance_ok and pitch_ok
    overall_ok = lap_length_ok and bolts_ok and detailing_ok

    return {
        "method": "Purlin lap/splice bolt group check at support",
        "provided_lap_mm": provided_lap_mm,
        "recommended_lap_mm": recommended_lap_mm,
        "lap_length_ok": lap_length_ok,
        "bolt_dia_mm": d,
        "hole_dia_mm": hole_dia,
        "bolt_rows": rows,
        "bolts_per_row": per_row,
        "bolt_count": bolt_count,
        "bolt_grade_fub": bolt_grade_fub,
        "plate_fu": plate_fu,
        "connected_thickness_mm": t,
        "edge_mm": edge_mm,
        "pitch_mm": pitch_mm,
        "kb": kb,
        "threads_area_mm2": threads_area,
        "shank_area_mm2": shank_area,
        "bolt_shear_capacity_kN": shear_capacity_kN,
        "bolt_bearing_capacity_kN": bearing_capacity_kN,
        "bolt_capacity_kN": bolt_capacity_kN,
        "support_reaction_kN": support_reaction_kN,
        "demand_per_bolt_kN": demand_per_bolt_kN,
        "group_capacity_kN": group_capacity_kN,
        "bolt_utilisation": bolt_utilisation,
        "bolts_ok": bolts_ok,
        "end_distance_ok": end_distance_ok,
        "pitch_ok": pitch_ok,
        "detailing_ok": detailing_ok,
        "overall_ok": overall_ok,
        "note": (
            "Recommended lap length is the greater of 10% of span and 600 mm. "
            "Bolt action uses the resultant support reaction from the governing load case."
        ),
    }


def run_purlin_design(inp: dict[str, Any]) -> dict[str, Any]:
    """Run purlin design checks and return all values needed by UI/PDF.

    Input keys mirror the Streamlit controls.  Returned values are intentionally
    verbose so formula blocks, summary tables, and reports do not recalculate or
    diverge from the governing design result.
    """
    sp = dict(inp.get("section_props") or {})

    span_m = _as_float(inp.get("span_m"), 5.0)
    spacing_m = _as_float(inp.get("spacing_m"), 1.5)
    slope_deg = _as_float(inp.get("roof_slope_deg", inp.get("slope_deg")), 10.0)
    dead_load = _as_float(inp.get("dead_load"), 0.55)
    live_load = _as_float(inp.get("live_load"), 0.75)
    wind_pressure = _as_float(inp.get("wind_pressure"), 0.70)
    cpe = _as_float(inp.get("Cp_ext", inp.get("Cpe")), -0.8)
    cpi = _as_float(inp.get("Cp_int", inp.get("Cpi")), 0.2)
    fy = _as_float(inp.get("fy"), 250.0)
    gm0 = _as_float(inp.get("gm0"), 1.10)
    requested_design_code = inp.get("design_code")
    requested_design_code = (
        str(requested_design_code).strip()
        if requested_design_code is not None
        else None
    )
    lap_length_m = _as_float(inp.get("lap_length_m"), max(0.10 * span_m, 0.60))
    lap_bolt_dia_mm = _as_float(inp.get("lap_bolt_dia_mm"), 16.0)
    lap_bolt_rows = _as_float(inp.get("lap_bolt_rows"), 2.0)
    lap_bolts_per_row = _as_float(inp.get("lap_bolts_per_row"), 2.0)
    lap_bolt_grade_fub = _as_float(inp.get("lap_bolt_grade_fub"), 400.0)
    lap_plate_fu = _as_float(inp.get("lap_plate_fu"), 410.0)

    theta = math.radians(slope_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # kg/m × g / 1000 = kN/m.
    sw_kNm = _as_float(sp.get("weight")) * 9.81 / 1000.0
    w_dl_total = dead_load * spacing_m + sw_kNm
    w_ll_total = live_load * spacing_m

    wz_DL = w_dl_total * cos_t
    wy_DL = w_dl_total * sin_t
    wz_LL = w_ll_total * cos_t
    wy_LL = w_ll_total * sin_t

    # Net wind is taken normal to the roof sheeting.  Negative values indicate
    # uplift/suction; design effects use absolute governing magnitudes below.
    w_wind = wind_pressure * (cpe - cpi) * spacing_m

    signed_combos = {
        "LC1: 1.5(DL+LL)": (1.5 * (wz_DL + wz_LL), 1.5 * (wy_DL + wy_LL)),
        "LC2: 1.2(DL+LL+Wind)": (1.2 * (wz_DL + wz_LL + w_wind), 1.2 * (wy_DL + wy_LL)),
        "LC3: 0.9DL+1.5Wind": (0.9 * wz_DL + 1.5 * w_wind, 0.9 * wy_DL),
    }
    governing_combo, (wz_signed, wy_signed) = max(
        signed_combos.items(), key=lambda item: abs(item[1][0]) + abs(item[1][1])
    )
    wz_d = abs(wz_signed)
    wy_d = abs(wy_signed)

    Mz_kNm = wz_d * span_m**2 / 8.0
    My_kNm = wy_d * span_m**2 / 8.0
    Vz_kN = wz_d * span_m / 2.0
    Vy_kN = wy_d * span_m / 2.0

    cls = _section_classification(sp, fy)
    use_plastic = cls["overall"] in ("Plastic", "Compact") and bool(
        sp.get("allow_plastic", True)
    )
    z_major = _as_float(sp.get("Zpx" if use_plastic else "Zxx"))
    z_minor = _as_float(sp.get("Zpy" if use_plastic else "Zyy"))

    E = 2.0e5  # MPa = N/mm²
    L_mm = span_m * 1000.0
    service_w = wz_DL + wz_LL  # kN/m == N/mm
    cold_formed = sp.get("section_family") in COLD_FORMED_FAMILIES
    # Preserve legacy/API behavior: cold-formed C/Z sections use IS 801
    # effective-width checks unless the caller explicitly requests IS 800.
    # The Streamlit UI always sends an explicit selection.
    design_code = (
        "IS 801:1975"
        if cold_formed and requested_design_code != "IS 800:2007"
        else "IS 800:2007"
    )
    cold_formed_checks: dict[str, Any] = {}

    Mdz_kNm = z_major * fy / (gm0 * 1000.0) if gm0 else 0.0
    Mdy_kNm = z_minor * fy / (gm0 * 1000.0) if gm0 else 0.0
    biaxial_ratio = _safe_ratio(My_kNm, Mdy_kNm) + _safe_ratio(Mz_kNm, Mdz_kNm)

    Av_mm2 = _as_float(sp.get("Av"), _as_float(sp.get("h")) * _as_float(sp.get("tw")))
    Vd_kN = Av_mm2 * fy / (math.sqrt(3.0) * gm0 * 1000.0) if gm0 else 0.0
    shear_ratio = _safe_ratio(Vz_kN, Vd_kN)
    Ixx_design_cm4 = _as_float(sp.get("Ixx"))

    if design_code == "IS 801:1975":
        cold_formed_checks = _cold_formed_design_checks(
            sp, fy, gm0, Mz_kNm, My_kNm, Vz_kN, service_w, L_mm
        )
        use_plastic = False
        z_major = cold_formed_checks["Zxx_eff"]
        z_minor = cold_formed_checks["Zyy_eff"]
        Mdz_kNm = cold_formed_checks["Mdz_eff_kNm"]
        Mdy_kNm = cold_formed_checks["Mdy_eff_kNm"]
        biaxial_ratio = cold_formed_checks["bending_ratio"]
        Vd_kN = cold_formed_checks["Vd_shear_kN"]
        shear_ratio = cold_formed_checks["shear_ratio"]
        Ixx_design_cm4 = cold_formed_checks["Ixx_eff"]

    biaxial_ok = biaxial_ratio <= 1.0 and cls["overall"] != "Slender"
    shear_ok = shear_ratio <= 1.0

    Ixx_mm4 = Ixx_design_cm4 * 1.0e4
    delta_max_mm = (
        (5.0 * service_w * L_mm**4 / (384.0 * E * Ixx_mm4)) if Ixx_mm4 else math.inf
    )
    if design_code == "IS 801:1975" and cold_formed_checks:
        cold_formed_checks["delta_eff_mm"] = delta_max_mm
    delta_limit_mm = L_mm / 180.0
    defl_ratio = _safe_ratio(delta_max_mm, delta_limit_mm)
    defl_ok = defl_ratio <= 1.0
    if design_code == "IS 801:1975" and cold_formed_checks:
        cold_formed_checks["checks"]["serviceability_ok"] = defl_ok
        cold_formed_checks["checks"]["overall_ok"] = all(
            cold_formed_checks["checks"].values()
        )

    lap_design = _bolt_lap_design(
        sp,
        Vz_kN,
        Vy_kN,
        span_m,
        lap_length_m,
        lap_bolt_dia_mm,
        lap_bolt_rows,
        lap_bolts_per_row,
        lap_bolt_grade_fub,
        lap_plate_fu,
    )

    checks_ok = [
        biaxial_ok,
        shear_ok,
        defl_ok,
        cls["overall"] != "Slender",
        lap_design["overall_ok"],
    ]
    if design_code == "IS 801:1975":
        checks_ok.append(bool(cold_formed_checks.get("checks", {}).get("overall_ok")))
    overall_status = "SAFE" if all(checks_ok) else "UNSAFE"

    wz_values = list(signed_combos.values())
    return {
        "status": "Purlin calculations complete.",
        "overall_status": overall_status,
        "section_name": inp.get("section_name", "Unknown Section"),
        "section_props": sp,
        "span_m": span_m,
        "spacing_m": spacing_m,
        "slope_deg": slope_deg,
        "dead_load": dead_load,
        "live_load": live_load,
        "wind_pressure": wind_pressure,
        "Cpe": cpe,
        "Cpi": cpi,
        "Cp_net": cpe - cpi,
        "fy": fy,
        "gm0": gm0,
        "sw_kNm": sw_kNm,
        "w_dl_total": w_dl_total,
        "w_ll_total": w_ll_total,
        "wz_DL": wz_DL,
        "wy_DL": wy_DL,
        "wz_LL": wz_LL,
        "wy_LL": wy_LL,
        "w_wind": w_wind,
        "w_wind_abs": abs(w_wind),
        "wz_1": wz_values[0][0],
        "wy_1": wz_values[0][1],
        "wz_2": wz_values[1][0],
        "wy_2": wz_values[1][1],
        "wz_3": wz_values[2][0],
        "wy_3": wz_values[2][1],
        "wz_d_signed": wz_signed,
        "wy_d_signed": wy_signed,
        "wz_d": wz_d,
        "wy_d": wy_d,
        "governing_combo": governing_combo,
        "Mz_kNm": Mz_kNm,
        "My_kNm": My_kNm,
        "Vz_kN": Vz_kN,
        "Vy_kN": Vy_kN,
        "section_class": cls,
        "design_code": design_code,
        "design_standard": (
            sp.get("design_standard", "IS 801:1975 effective-width cold-formed design")
            if design_code == "IS 801:1975"
            else "IS 800:2007 gross-section steel design check"
        ),
        "design_note": sp.get("design_note", ""),
        "use_plastic_modulus": use_plastic,
        "cold_formed_checks": cold_formed_checks,
        "z_major_design": z_major,
        "z_minor_design": z_minor,
        "Ixx_design_cm4": Ixx_design_cm4,
        "Mdz_kNm": Mdz_kNm,
        "Mdy_kNm": Mdy_kNm,
        "biaxial_ratio": biaxial_ratio,
        "biaxial_ok": biaxial_ok,
        "Av_mm2": Av_mm2,
        "Vd_kN": Vd_kN,
        "shear_ratio": shear_ratio,
        "shear_ok": shear_ok,
        "delta_max_mm": delta_max_mm,
        "delta_limit_mm": delta_limit_mm,
        "defl_ratio": defl_ratio,
        "defl_ok": defl_ok,
        "lap_design": lap_design,
    }
