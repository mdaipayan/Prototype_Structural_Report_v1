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
        "fy": 250.0, 
        
        # --- Add these to prevent ZeroDivisionError in the Summary Table ---
        "Vd_kN": 100.0,         # Denominator for Shear Check
        "delta_limit_mm": 25.0, # Denominator for Deflection Check
        # -------------------------------------------------------------------
        
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
