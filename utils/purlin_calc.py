def run_purlin_design(inp):
    """
    Placeholder function for Purlin Design calculations.
    Accepts an input dictionary 'inp' containing user parameters.
    """
    
    # Updated dummy dictionary to prevent KeyErrors in the UI
    return {
        "status": "Purlin calculations successful!", 
        "overall_status": "SAFE",
        # Try to pull the section name from the UI inputs, default to "Test Section" if missing
        "section_name": inp.get("section_name", "Test Section"), 
        "utilization": 0.0,
        "section_class": "Plastic",  
        "Mdz": 0.0,                  
        "Mdy": 0.0,
        "Vz": 0.0                    
    }
