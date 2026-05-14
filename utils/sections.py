"""
Standard Structural Steel Sections as per IS 808.
Units:
- Depth (h): mm
- Flange Width (bf): mm
- Web Thickness (tw): mm
- Flange Thickness (tf): mm
- Area (Area): cm^2
- Weight (weight): kg/m
- Moment of Inertia (Ixx, Iyy): cm^4
- Elastic Section Modulus (Zxx, Zyy): cm^3
- Plastic Section Modulus (Zpx, Zpy): cm^3
"""

# Indian Standard Medium Weight Beams
ISMB = {
    "ISMB 100": {
        "h": 100,
        "bf": 50,
        "tw": 4.0,
        "tf": 7.0,
        "Area": 11.4,
        "weight": 8.9,
        "Ixx": 183.0,
        "Iyy": 12.9,
        "Zxx": 36.6,
        "Zyy": 5.16,
        "Zpx": 41.7,
        "Zpy": 8.0,
    },
    "ISMB 150": {
        "h": 150,
        "bf": 75,
        "tw": 5.0,
        "tf": 8.0,
        "Area": 19.1,
        "weight": 15.0,
        "Ixx": 718.0,
        "Iyy": 46.8,
        "Zxx": 95.7,
        "Zyy": 12.48,
        "Zpx": 109.1,
        "Zpy": 19.3,
    },
    "ISMB 200": {
        "h": 200,
        "bf": 100,
        "tw": 5.7,
        "tf": 10.8,
        "Area": 32.3,
        "weight": 25.4,
        "Ixx": 2235.0,
        "Iyy": 150.0,
        "Zxx": 223.5,
        "Zyy": 30.0,
        "Zpx": 254.8,
        "Zpy": 46.5,
    },
    "ISMB 250": {
        "h": 250,
        "bf": 125,
        "tw": 6.9,
        "tf": 12.5,
        "Area": 47.5,
        "weight": 37.3,
        "Ixx": 5130.0,
        "Iyy": 334.0,
        "Zxx": 410.4,
        "Zyy": 53.44,
        "Zpx": 467.9,
        "Zpy": 82.8,
    },
    "ISMB 300": {
        "h": 300,
        "bf": 140,
        "tw": 7.5,
        "tf": 12.4,
        "Area": 56.2,
        "weight": 44.2,
        "Ixx": 8603.0,
        "Iyy": 453.0,
        "Zxx": 573.5,
        "Zyy": 64.71,
        "Zpx": 653.8,
        "Zpy": 100.3,
    },
    "ISMB 400": {
        "h": 400,
        "bf": 140,
        "tw": 8.9,
        "tf": 16.0,
        "Area": 78.4,
        "weight": 61.6,
        "Ixx": 20458.0,
        "Iyy": 622.0,
        "Zxx": 1022.9,
        "Zyy": 88.86,
        "Zpx": 1166.1,
        "Zpy": 137.7,
    },
}

# Indian Standard Light Weight Beams
ISLB = {
    "ISLB 100": {
        "h": 100,
        "bf": 50,
        "tw": 4.0,
        "tf": 5.3,
        "Area": 10.2,
        "weight": 8.0,
        "Ixx": 165.0,
        "Iyy": 11.4,
        "Zxx": 33.0,
        "Zyy": 4.56,
        "Zpx": 37.6,
        "Zpy": 7.1,
    },
    "ISLB 150": {
        "h": 150,
        "bf": 80,
        "tw": 4.8,
        "tf": 5.8,
        "Area": 18.0,
        "weight": 14.2,
        "Ixx": 688.0,
        "Iyy": 55.0,
        "Zxx": 91.7,
        "Zyy": 13.75,
        "Zpx": 104.6,
        "Zpy": 21.3,
    },
    "ISLB 200": {
        "h": 200,
        "bf": 100,
        "tw": 5.4,
        "tf": 7.3,
        "Area": 25.2,
        "weight": 19.8,
        "Ixx": 1696.0,
        "Iyy": 115.0,
        "Zxx": 169.6,
        "Zyy": 23.0,
        "Zpx": 193.3,
        "Zpy": 35.7,
    },
    "ISLB 250": {
        "h": 250,
        "bf": 125,
        "tw": 6.1,
        "tf": 8.2,
        "Area": 35.5,
        "weight": 27.9,
        "Ixx": 3717.0,
        "Iyy": 268.0,
        "Zxx": 297.4,
        "Zyy": 42.88,
        "Zpx": 339.0,
        "Zpy": 66.5,
    },
}

# Indian Standard Medium Weight Channels
ISMC = {
    "ISMC 100": {
        "h": 100,
        "bf": 50,
        "tw": 4.7,
        "tf": 7.5,
        "Area": 11.7,
        "weight": 9.2,
        "Ixx": 192.0,
        "Iyy": 27.5,
        "Zxx": 38.4,
        "Zyy": 11.0,
        "Zpx": 43.8,
        "Zpy": 19.3,
    },
    "ISMC 150": {
        "h": 150,
        "bf": 75,
        "tw": 5.4,
        "tf": 9.0,
        "Area": 20.8,
        "weight": 16.4,
        "Ixx": 788.0,
        "Iyy": 116.0,
        "Zxx": 105.1,
        "Zyy": 30.93,
        "Zpx": 119.8,
        "Zpy": 54.1,
    },
    "ISMC 200": {
        "h": 200,
        "bf": 75,
        "tw": 6.1,
        "tf": 11.4,
        "Area": 28.2,
        "weight": 22.1,
        "Ixx": 1830.0,
        "Iyy": 153.0,
        "Zxx": 183.0,
        "Zyy": 40.8,
        "Zpx": 208.6,
        "Zpy": 71.4,
    },
    "ISMC 250": {
        "h": 250,
        "bf": 80,
        "tw": 7.1,
        "tf": 14.1,
        "Area": 38.6,
        "weight": 30.4,
        "Ixx": 3880.0,
        "Iyy": 211.0,
        "Zxx": 310.4,
        "Zyy": 52.75,
        "Zpx": 353.9,
        "Zpy": 92.3,
    },
    "ISMC 300": {
        "h": 300,
        "bf": 90,
        "tw": 7.6,
        "tf": 13.6,
        "Area": 45.6,
        "weight": 35.8,
        "Ixx": 6362.0,
        "Iyy": 310.0,
        "Zxx": 424.1,
        "Zyy": 68.89,
        "Zpx": 483.5,
        "Zpy": 120.6,
    },
}


STEEL_DENSITY_KG_PER_MM2_M = 0.00785


def _finalize_section(props: dict) -> dict:
    """Return a section-property dict with defaults required by purlin design."""
    out = dict(props)
    out.setdefault("Zpx", out["Zxx"])
    out.setdefault("Zpy", out["Zyy"])
    out.setdefault("Av", out.get("h", 0.0) * out.get("tw", 0.0))
    out.setdefault("allow_plastic", False)
    out.setdefault("section_class_override", "Semi-compact")
    return out


def _area_weight(area_mm2: float) -> tuple[float, float]:
    return area_mm2 / 100.0, area_mm2 * STEEL_DENSITY_KG_PER_MM2_M


def _equal_angle_section(leg_mm: float, thickness_mm: float) -> dict:
    """Approximate equal angle properties from two rectangular legs minus overlap."""
    a = leg_mm
    t = thickness_mm
    pieces = [
        (t, a, t / 2.0, a / 2.0),
        (a, t, a / 2.0, t / 2.0),
        (-t, -t, t / 2.0, t / 2.0),
    ]
    area = sum(w * h for w, h, _, _ in pieces)
    cx = sum(w * h * x for w, h, x, _ in pieces) / area
    cy = sum(w * h * y for w, h, _, y in pieces) / area
    ixx = sum((w * h**3 / 12.0) + w * h * (y - cy) ** 2 for w, h, _, y in pieces)
    iyy = sum((h * w**3 / 12.0) + w * h * (x - cx) ** 2 for w, h, x, _ in pieces)
    zxx = ixx / max(cy, a - cy)
    zyy = iyy / max(cx, a - cx)
    area_cm2, weight = _area_weight(area)
    return _finalize_section(
        {
            "h": a,
            "bf": a,
            "tw": t,
            "tf": t,
            "Area": round(area_cm2, 2),
            "weight": round(weight, 2),
            "Ixx": round(ixx / 1.0e4, 2),
            "Iyy": round(iyy / 1.0e4, 2),
            "Zxx": round(zxx / 1000.0, 2),
            "Zyy": round(zyy / 1000.0, 2),
            "Zpx": round(1.12 * zxx / 1000.0, 2),
            "Zpy": round(1.12 * zyy / 1000.0, 2),
            "Av": round(a * t, 2),
            "section_family": "Angle sections",
            "shape": "L-shape",
            "design_note": "Gross equal-angle properties; connection eccentricity and principal-axis bending must be checked for final design.",
            "ui_note": "Gross angle-section check. Verify connection eccentricity and principal-axis bending before final design.",
        }
    )


def _cold_formed_c_section(
    depth_mm: float, flange_mm: float, lip_mm: float, thickness_mm: float
) -> dict:
    """Approximate lipped C properties using flat plate elements without corner radii."""
    h = depth_mm
    b = flange_mm
    lip = lip_mm
    t = thickness_mm
    pieces = [
        (t, h, t / 2.0, h / 2.0),
        (b, t, t + b / 2.0, h - t / 2.0),
        (b, t, t + b / 2.0, t / 2.0),
        (t, lip, t + b - t / 2.0, h - t - lip / 2.0),
        (t, lip, t + b - t / 2.0, t + lip / 2.0),
    ]
    area = sum(w * hh for w, hh, _, _ in pieces)
    cx = sum(w * hh * x for w, hh, x, _ in pieces) / area
    cy = h / 2.0
    ixx = sum((w * hh**3 / 12.0) + w * hh * (y - cy) ** 2 for w, hh, _, y in pieces)
    iyy = sum((hh * w**3 / 12.0) + w * hh * (x - cx) ** 2 for w, hh, x, _ in pieces)
    zxx = ixx / (h / 2.0)
    zyy = iyy / max(cx, t + b - cx)
    area_cm2, weight = _area_weight(area)
    return _finalize_section(
        {
            "h": h,
            "bf": b,
            "tw": t,
            "tf": t,
            "lip": lip,
            "Area": round(area_cm2, 2),
            "weight": round(weight, 2),
            "Ixx": round(ixx / 1.0e4, 2),
            "Iyy": round(iyy / 1.0e4, 2),
            "Zxx": round(zxx / 1000.0, 2),
            "Zyy": round(zyy / 1000.0, 2),
            "Av": round(h * t, 2),
            "section_family": "Cold-formed C-sections",
            "shape": "Lipped C",
            "design_standard": "IS 801 effective-width cold-formed design",
            "design_note": "Cold-formed lipped C design uses effective-width local buckling, shear buckling, web crippling, distortional geometry, and serviceability checks.",
            "ui_note": "Effective-width cold-formed design: local buckling, shear buckling, web crippling, distortional geometry, and deflection checks included.",
        }
    )


def _cold_formed_z_section(
    depth_mm: float, flange_mm: float, lip_mm: float, thickness_mm: float
) -> dict:
    """Approximate lipped Z properties using flat plate elements without corner radii."""
    props = _cold_formed_c_section(depth_mm, flange_mm, lip_mm, thickness_mm)
    props.update(
        {
            "section_family": "Cold-formed Z-sections",
            "shape": "Lipped Z",
            "Iyy": round(props["Iyy"] * 0.92, 2),
            "Zyy": round(props["Zyy"] * 0.92, 2),
            "Zpy": round(props["Zyy"] * 0.92, 2),
            "design_standard": "IS 801 effective-width cold-formed design",
            "design_note": "Cold-formed lipped Z design uses effective-width local buckling, shear buckling, web crippling, distortional geometry, lap-continuity metadata, and serviceability checks.",
            "ui_note": "Effective-width lipped Z design: local buckling, shear buckling, web crippling, distortional geometry, lap-continuity, and deflection checks included.",
        }
    )
    return props


def _rhs_section(depth_mm: float, width_mm: float, thickness_mm: float) -> dict:
    """Rectangular/square hollow section properties from outside dimensions."""
    h = depth_mm
    b = width_mm
    t = thickness_mm
    hi = max(h - 2.0 * t, 0.0)
    bi = max(b - 2.0 * t, 0.0)
    area = b * h - bi * hi
    ixx = (b * h**3 - bi * hi**3) / 12.0
    iyy = (h * b**3 - hi * bi**3) / 12.0
    zxx = ixx / (h / 2.0)
    zyy = iyy / (b / 2.0)
    area_cm2, weight = _area_weight(area)
    return _finalize_section(
        {
            "h": h,
            "bf": b,
            "tw": t,
            "tf": t,
            "Area": round(area_cm2, 2),
            "weight": round(weight, 2),
            "Ixx": round(ixx / 1.0e4, 2),
            "Iyy": round(iyy / 1.0e4, 2),
            "Zxx": round(zxx / 1000.0, 2),
            "Zyy": round(zyy / 1000.0, 2),
            "Zpx": round(1.15 * zxx / 1000.0, 2),
            "Zpy": round(1.15 * zyy / 1000.0, 2),
            "Av": round(2.0 * h * t, 2),
            "section_family": "Hollow / box sections",
            "shape": "RHS / SHS",
            "section_class_override": "Compact",
            "design_standard": "IS 4923 / IS 800 gross-section check",
            "design_note": "Hollow section properties based on nominal outside dimensions and wall thickness.",
            "ui_note": "Hollow section check based on nominal outside dimensions and wall thickness.",
        }
    )


# Indian Standard Angle Sections (equal angles) for purlin design selection.
ISA = {
    "ISA 50x50x6": _equal_angle_section(50, 6),
    "ISA 65x65x6": _equal_angle_section(65, 6),
    "ISA 75x75x8": _equal_angle_section(75, 8),
    "ISA 90x90x8": _equal_angle_section(90, 8),
    "ISA 100x100x10": _equal_angle_section(100, 10),
}

# Cold-formed lipped C purlins.  Dimensions are nominal flat-element sizes.
COLD_FORMED_C = {
    "CFLC 150x60x20x2.0": _cold_formed_c_section(150, 60, 20, 2.0),
    "CFLC 175x65x20x2.0": _cold_formed_c_section(175, 65, 20, 2.0),
    "CFLC 200x70x20x2.5": _cold_formed_c_section(200, 70, 20, 2.5),
    "CFLC 250x75x25x2.5": _cold_formed_c_section(250, 75, 25, 2.5),
    "CFLC 300x80x25x3.0": _cold_formed_c_section(300, 80, 25, 3.0),
}

# Cold-formed lipped Z purlins.  Dimensions are nominal flat-element sizes.
COLD_FORMED_Z = {
    "CFLZ 150x60x20x2.0": _cold_formed_z_section(150, 60, 20, 2.0),
    "CFLZ 175x65x20x2.0": _cold_formed_z_section(175, 65, 20, 2.0),
    "CFLZ 200x70x20x2.5": _cold_formed_z_section(200, 70, 20, 2.5),
    "CFLZ 250x75x25x2.5": _cold_formed_z_section(250, 75, 25, 2.5),
    "CFLZ 300x80x25x3.0": _cold_formed_z_section(300, 80, 25, 3.0),
}

# Rectangular/square hollow purlin sections based on nominal outside dimensions.
HOLLOW_BOX = {
    "RHS 100x50x3.2": _rhs_section(100, 50, 3.2),
    "RHS 150x75x4.0": _rhs_section(150, 75, 4.0),
    "RHS 200x100x5.0": _rhs_section(200, 100, 5.0),
    "SHS 100x100x4.0": _rhs_section(100, 100, 4.0),
    "SHS 150x150x5.0": _rhs_section(150, 150, 5.0),
}


# Common purlin section families used in IS-based steel roof framing.
# Rolled-section properties below are tabulated as per IS 808 / SP 6(1);
# angle/cold-formed/tubular additions provide gross-section properties for
# preliminary purlin design and should be verified against final IS checks.
COMMON_PURLIN_SECTION_TYPES = [
    {
        "type": "Channel sections",
        "shape": "C-channel / U-channel",
        "designation": "ISMC / ISLC",
        "examples": "ISMC 100, ISMC 150, ISMC 200",
        "typical_use": "Most common rolled purlin option for roof sheeting support and simple rafter connections.",
        "calculation_status": "Available for design when present in ISMC table",
    },
    {
        "type": "Beam / I-sections",
        "shape": "I-shape / beam profile",
        "designation": "ISMB / ISLB",
        "examples": "ISMB 150, ISMB 200, ISLB 200",
        "typical_use": "Used where longer spans, heavier roof loads, or higher wind effects require greater flexural stiffness.",
        "calculation_status": "Available for design when present in ISMB/ISLB tables",
    },
    {
        "type": "Angle sections",
        "shape": "L-shape / double-angle",
        "designation": "ISA",
        "examples": "ISA 50x50x6, ISA 75x75x8, ISA 100x100x10",
        "typical_use": "Economical for lighter roofs and shorter spans; often adopted as single or back-to-back double angles.",
        "calculation_status": "Available for design with gross angle-section properties",
    },
    {
        "type": "Cold-formed C-sections",
        "shape": "C-shape / lipped channel",
        "designation": "C / lipped C",
        "examples": "CFLC 150x60x20x2.0, CFLC 200x70x20x2.5",
        "typical_use": "Common in light-gauge and pre-engineered building roof systems.",
        "calculation_status": "Available with effective-width cold-formed design checks",
    },
    {
        "type": "Cold-formed Z-sections",
        "shape": "Z-shape / lipped Z",
        "designation": "Z / lipped Z",
        "examples": "CFLZ 150x60x20x2.0, CFLZ 200x70x20x2.5",
        "typical_use": "Preferred for continuous purlin lines and lap connections over supports in PEB roofs.",
        "calculation_status": "Available with effective-width cold-formed design checks",
    },
    {
        "type": "Hollow / box sections",
        "shape": "RHS / SHS / box profile",
        "designation": "IS 4923 tubular sections",
        "examples": "RHS 150x75x4.0, RHS 200x100x5.0, SHS 100x100x4.0",
        "typical_use": "Occasionally used where torsional stiffness, closed profiles, or architectural exposed framing are required.",
        "calculation_status": "Available for design with hollow-section properties",
    },
]

# Combine all dictionaries into one master lookup variable
ALL_SECTIONS = {}
ALL_SECTIONS.update(ISMB)
ALL_SECTIONS.update(ISLB)
ALL_SECTIONS.update(ISMC)
ALL_SECTIONS.update(ISA)
ALL_SECTIONS.update(COLD_FORMED_C)
ALL_SECTIONS.update(COLD_FORMED_Z)
ALL_SECTIONS.update(HOLLOW_BOX)
