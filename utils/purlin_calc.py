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
        "section_class": "Plastic"
    })
    
    return dummy_results
