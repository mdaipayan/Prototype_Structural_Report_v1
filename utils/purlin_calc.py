from collections import defaultdict

def run_purlin_design(inp):
    """
    Placeholder function for Purlin Design calculations.
    """
    # Create a dictionary that automatically returns 0.0 for any missing number keys
    dummy_results = defaultdict(lambda: 0.0)
    
    # Add the specific strings your UI requires
    dummy_results.update({
        "status": "Purlin calculations successful!", 
        "overall_status": "SAFE",
        "section_name": inp.get("section_name", "Test Section"),
        
        # ADD THIS LINE: Pass the section properties back to the UI/PDF!
        "section_props": inp.get("section_props", {"Area": 0.0, "h": 0.0, "bf": 0.0, "tf": 0.0, "tw": 0.0}),
        
        "fy": 250.0, 
        "Vd_kN": 100.0, 
        "delta_limit_mm": 25.0,
        
        "section_class": {
            "name": "Plastic", 
            "epsilon": 1.0, 
            "class_type": 1,
            "overall": "Plastic",
            "b_tf": 8.5,
            "d_tw": 40.0,
            "flange_class": "Plastic",
            "web_class": "Plastic",
            "limits": {
                "flange": [9.4, 13.6, 15.7],
                "web": [84.0, 105.0, 126.0]
            }
        } 
    })
    
    # Correctly indented return statement
    return dummy_results
