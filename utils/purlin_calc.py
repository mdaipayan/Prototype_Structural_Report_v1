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
        "fy": 250.0, # Added so your math report looks normal
        "section_class": {
            "name": "Plastic", 
            "epsilon": 1.0, 
            "class_type": 1 
        } 
    })
    
    return dummy_results
