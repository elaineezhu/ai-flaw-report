def determine_report_types(involves_real_world_incident, involves_threat_actor):
    """Determine report types based on the answers to key questions"""
    report_types = []
    
    # Only determine report types if both questions have been answered
    if involves_real_world_incident is not None and involves_threat_actor is not None:
        if involves_real_world_incident and involves_threat_actor:
            report_types = ["Real-World Events", "Malign Actor", "Security Incident Report"]
        elif involves_real_world_incident:
            report_types = ["Real-World Events"]
        elif involves_threat_actor:
            report_types = ["Malign Actor", "Vulnerability Report"]
        else:
            report_types = ["Hazard Report"]
    
    return report_types