"""
Standard Structural Steel Sections as per IS 808.
Units:
- Depth (D): mm
- Flange Width (B): mm
- Web Thickness (tw): mm
- Flange Thickness (tf): mm
- Area (A): cm^2
- Weight: kg/m
- Moment of Inertia (Ixx, Iyy): cm^4
"""

# Indian Standard Medium Weight Beams
ISMB = {
    "ISMB 100": {"D": 100, "B": 50, "tw": 4.0, "tf": 7.0, "Area": 11.4, "Weight": 8.9, "Ixx": 183.0, "Iyy": 12.9},
    "ISMB 150": {"D": 150, "B": 75, "tw": 5.0, "tf": 8.0, "Area": 19.1, "Weight": 15.0, "Ixx": 718.0, "Iyy": 46.8},
    "ISMB 200": {"D": 200, "B": 100, "tw": 5.7, "tf": 10.8, "Area": 32.3, "Weight": 25.4, "Ixx": 2235.0, "Iyy": 150.0},
    "ISMB 250": {"D": 250, "B": 125, "tw": 6.9, "tf": 12.5, "Area": 47.5, "Weight": 37.3, "Ixx": 5130.0, "Iyy": 334.0},
    "ISMB 300": {"D": 300, "B": 140, "tw": 7.5, "tf": 12.4, "Area": 56.2, "Weight": 44.2, "Ixx": 8603.0, "Iyy": 453.0},
    "ISMB 400": {"D": 400, "B": 140, "tw": 8.9, "tf": 16.0, "Area": 78.4, "Weight": 61.6, "Ixx": 20458.0, "Iyy": 622.0},
}

# Indian Standard Light Weight Beams
ISLB = {
    "ISLB 100": {"D": 100, "B": 50, "tw": 4.0, "tf": 5.3, "Area": 10.2, "Weight": 8.0, "Ixx": 165.0, "Iyy": 11.4},
    "ISLB 150": {"D": 150, "B": 80, "tw": 4.8, "tf": 5.8, "Area": 18.0, "Weight": 14.2, "Ixx": 688.0, "Iyy": 55.0},
    "ISLB 200": {"D": 200, "B": 100, "tw": 5.4, "tf": 7.3, "Area": 25.2, "Weight": 19.8, "Ixx": 1696.0, "Iyy": 115.0},
    "ISLB 250": {"D": 250, "B": 125, "tw": 6.1, "tf": 8.2, "Area": 35.5, "Weight": 27.9, "Ixx": 3717.0, "Iyy": 268.0},
}

# Indian Standard Medium Weight Channels
ISMC = {
    "ISMC 100": {"D": 100, "B": 50, "tw": 4.7, "tf": 7.5, "Area": 11.7, "Weight": 9.2, "Ixx": 192.0, "Iyy": 27.5},
    "ISMC 150": {"D": 150, "B": 75, "tw": 5.4, "tf": 9.0, "Area": 20.8, "Weight": 16.4, "Ixx": 788.0, "Iyy": 116.0},
    "ISMC 200": {"D": 200, "B": 75, "tw": 6.1, "tf": 11.4, "Area": 28.2, "Weight": 22.1, "Ixx": 1830.0, "Iyy": 153.0},
    "ISMC 250": {"D": 250, "B": 80, "tw": 7.1, "tf": 14.1, "Area": 38.6, "Weight": 30.4, "Ixx": 3880.0, "Iyy": 211.0},
    "ISMC 300": {"D": 300, "B": 90, "tw": 7.6, "tf": 13.6, "Area": 45.6, "Weight": 35.8, "Ixx": 6362.0, "Iyy": 310.0},
}

# Combine all dictionaries into one master lookup variable
ALL_SECTIONS = {}
ALL_SECTIONS.update(ISMB)
ALL_SECTIONS.update(ISLB)
ALL_SECTIONS.update(ISMC)
