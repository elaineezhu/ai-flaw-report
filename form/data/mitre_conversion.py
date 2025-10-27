import json
from pathlib import Path
from datetime import datetime, timezone

def _load_any(obj):
    """
    Accepts dict, path to JSON file, or JSON string.
    Returns a Python dict.
    """
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, (str, Path)):
        p = Path(str(obj))
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        try:
            return json.loads(str(obj))
        except json.JSONDecodeError as e:
            raise TypeError(
                "Input must be a dict, a path to a JSON file, or a JSON string."
            ) from e
    raise TypeError("Input must be a dict, a path to a JSON file, or a JSON string.")

def _first(lst, default=None):
    if isinstance(lst, list) and lst:
        return lst[0]
    return default

def _get_list(data: dict, *keys):
    for k in keys:
        if k in data and isinstance(data[k], list):
            return data[k]
    return []

def _get_str(data: dict, *keys, default=""):
    for k in keys:
        v = data.get(k)
        if isinstance(v, str) and v.strip() != "":
            return v
    return default

def _map_impacts_to_mitre(impacts: list) -> dict:
    """
    Map our impacts to MITRE categories.
    Returns: {assurance_categories, harm_categories, impact_types}
    """
    assurance_map = {
        "Security": "Security",
        "Privacy": "Privacy",
        "Discrimination/Bias": "Equitability",
        "Misinformation": "Reliability",
        "Safety": "Robustness"
    }
    
    harm_map = {
        "Discrimination/Bias": "Social",
        "Privacy": "Privacy/Harassment",
        "Misinformation": "Social",
        "Security": "Financial/Reputational",
        "Safety": "Physical/Environmental",
        "Environmental": "Physical/Environmental"
    }
    
    impact_map = {
        "Privacy": "Confidentiality/Privacy",
        "Security": "Integrity",
        "Misinformation": "Integrity",
        "Safety": "Availability"
    }
    
    assurance_cats = []
    harm_cats = []
    impact_types = []
    
    for impact in impacts:
        if impact in assurance_map:
            cat = assurance_map[impact]
            if cat not in assurance_cats:
                assurance_cats.append(cat)
        
        if impact in harm_map:
            cat = harm_map[impact]
            if cat not in harm_cats:
                harm_cats.append(cat)
        
        if impact in impact_map:
            cat = impact_map[impact]
            if cat not in impact_types:
                impact_types.append(cat)
    
    # Defaults
    if not assurance_cats:
        assurance_cats = ["Unknown"]
    if not harm_cats:
        harm_cats = ["Other"]
    if not impact_types:
        impact_types = ["Integrity"]
    
    return {
        "assurance": assurance_cats,
        "harm": harm_cats,
        "impact": impact_types
    }

def _map_severity(severity: str) -> str:
    """Map our severity to MITRE HarmSeverity enum."""
    severity_map = {
        "Critical": "Severe",
        "High": "Severe",
        "Significant": "Moderate",
        "Medium": "Moderate",
        "Low": "Minor",
        "Negligible": "Negligible"
    }
    return severity_map.get(severity, "Unknown")

def _map_lifecycle_phase(report_types: list) -> str:
    """Map report types to MITRE LifecyclePhase."""
    if "Real-World Incidents" in report_types:
        return "Deployment"
    elif "Vulnerability Report" in report_types:
        return "Quality Assurance"
    elif "Hazard Report" in report_types:
        return "Model Engineering"
    else:
        return "Model Engineering"

def _map_threat_actor_intent(report_types: list, attacker_objectives: list) -> list:
    """Determine threat actor intent."""
    if "Malign Actor" in report_types or "Security Incident Report" in report_types:
        return ["Deliberate"]
    elif attacker_objectives:
        return ["Deliberate"]
    else:
        return ["Unknown"]

def convert_to_mitre_atlas(raw_or_path) -> dict:
    """
    Converts AI flaw report to MITRE ATLAS V1 format.
    Accepts dict, path to JSON file, or JSON string.
    """
    data = _load_any(raw_or_path)
    
    report_id = _get_str(data, "Report ID", default=None)
    title = _get_str(data, "Flaw Description", "Incident Description", default="AI Incident Report")
    if len(title) > 100:
        title = title[:97] + "..."
    
    # Description
    description = _get_str(
        data,
        "Incident Description - Detailed",
        "Flaw Description - Detailed",
        "Incident Description",
        "Flaw Description",
        default="No description provided"
    )
    description = description.replace("**Detailed Description:**\n", "").strip()
    
    # Dates
    submission_timestamp = _get_str(data, "Submission Timestamp", default="")
    flaw_timestamp = _get_str(data, "Flaw Timestamp Start", default="")
    
    if submission_timestamp:
        date = submission_timestamp
    elif flaw_timestamp:
        date = flaw_timestamp
    else:
        date = datetime.now(timezone.utc).isoformat()
    
    start_date = flaw_timestamp if flaw_timestamp else date
    end_date = start_date
    
    report_types = _get_list(data, "Report Types")
    impacts = _get_list(data, "Impacts")
    specific_harms = _get_list(data, "Specific Harm Types")
    
    mitre_cats = _map_impacts_to_mitre(impacts)
    
    # Severity
    severity = _get_str(data, "Severity", default="Unknown")
    harm_severity = _map_severity(severity)
    
    # Geographic location
    incident_locations = _get_str(data, "Incident Location(s)", default=None)
    geo_locations = [incident_locations] if incident_locations else None
    
    # Affected entity
    systems = _get_list(data, "Systems")
    affected_entity = None
    if systems:
        # This is a simplified mapping
        vendor_map = {
            "GPT-3.5-Turbo": "OpenAI",
            "GPT-4": "OpenAI",
            "Claude": "Anthropic",
            "Gemini": "Google",
            "LLaMA": "Meta",
            "Copilot": "Microsoft"
        }
        first_system = systems[0]
        vendor = vendor_map.get(first_system, "Unknown")
        affected_entity = {
            "name": vendor,
            "primaryIndustry": "Technology",
            "secondaryIndustry": "Artificial Intelligence"
        }
    
    # Affected systems
    affected_systems = []
    for system in systems:
        affected_systems.append({
            "developer": vendor_map.get(system, "Unknown"),
            "name": system,
            "description": f"AI System: {system}",
            "technologyDomain": "Artificial Intelligence",
            "intendedUse": None,
            "actualUse": None,
            "levelOfAutonomy": None,
            "softwareSpecs": None,
            "hardwareSpecs": None
        })
    
    # Affected AI artifacts
    lifecycle_phase = _map_lifecycle_phase(report_types)
    affected_ai_artifacts = {
        "lifecyclePhase": lifecycle_phase,
        "dataTypes": "text",
        "dataset": None,
        "modelTask": None,
        "modelArchitecture": None,
        "modelSource": None
    }
    
    # Affected users
    stakeholders = _get_list(data, "Impacted Stakeholder(s)")
    affected_users = None
    if stakeholders:
        affected_users = {
            "impactedUserTypes": ", ".join(stakeholders),
            "numberOfDirectlyImpactedUsers": None,
            "numberOfIndirectlyImpactedUsers": None
        }
    
    # Detection details
    detection_methods = _get_list(data, "Detection")
    reporter_id = _get_str(data, "Reporter ID", default="Anonymous")
    
    detection = {
        "date": submission_timestamp if submission_timestamp else None,
        "reporter": reporter_id,
        "method": detection_methods if detection_methods else None,
        "methodDetail": None,
        "dataSource": None
    }
    
    # Mitigation
    mitigation = {
        "mitigationLevel": None,
        "date": None,
        "categories": None,
        "lifecyclePhase": None,
        "additionalDetails": None
    }
    
    response_details = {
        "detection": detection,
        "mitigation": mitigation
    }
    
    # Attack details
    attacker_resources = _get_list(data, "Attacker Resources")
    attacker_objectives = _get_list(data, "Attacker Objectives")
    poc = _get_str(data, "Proof-of-Concept Exploit", default="")
    
    attack_details = None
    if attacker_resources or attacker_objectives or poc:
        capabilities = []
        if attacker_resources:
            if any("training data" in r.lower() for r in attacker_resources):
                capabilities.append("Training Data Control")
            if any("model" in r.lower() for r in attacker_resources):
                capabilities.append("Model Control")
            if any("query" in r.lower() or "access" in r.lower() for r in attacker_resources):
                capabilities.append("Query Access")
        
        stage_of_learning = []
        if "Real-World Incidents" in report_types:
            stage_of_learning.append("Deployment")
        else:
            stage_of_learning.append("Training")
        
        attack_details = {
            "name": None,
            "attackDescription": _get_str(data, "Harm Narrative", "Context Info", default=None),
            "attackTechnique": None,
            "attackMechanism": None,
            "stageOfLearning": stage_of_learning if stage_of_learning else None,
            "capabilities": capabilities if capabilities else None,
            "knowledge": None,
            "knowledgeDetails": None,
            "procedure": poc if poc else None,
            "cost": None,
            "failureMode": None,
            "exfiltratedData": None
        }
    
    # Model information
    model_information = {
        "architecture": None,
        "source": None,
        "trainingSet": [],
        "failureMode": None,
        "artifacts": None
    }
    
    # External references
    external_refs = []
    context_info = _get_str(data, "Context Info", default="")
    if context_info:
        external_refs.append(context_info)
    
    # Meta information
    meta = {
        "incidentSharing": "MITRE Only",  # Default
        "tnc_agreed": True,
        "tnc_text": "AI Flaw Report submission"
    }
    
    # Contributor
    contributor = reporter_id
    
    # Investigation phase
    investigation_phase = "New"
    
    # Threat actor intent
    threat_actor_intent = _map_threat_actor_intent(report_types, attacker_objectives)
    
    # Build MITRE ATLAS report
    mitre_report = {
        "id": report_id,
        "title": title,
        "date": date,
        "description": description,
        "_meta": meta,
        "contributor": contributor,
        "status": "submitted",
        "startDate": start_date,
        "endDate": end_date,
        "investigationPhase": investigation_phase,
        "assuranceCategory": mitre_cats["assurance"],
        "threatActorIntent": threat_actor_intent,
        "harmCategories": mitre_cats["harm"],
        "harmSeverity": harm_severity,
        "impact": mitre_cats["impact"],
        "geographicLocation": geo_locations,
        "associatedVulnerabilities": None,
        "affectedEntity": affected_entity,
        "affectedSystems": affected_systems if affected_systems else None,
        "affectedAiArtifacts": affected_ai_artifacts,
        "affectedUsers": affected_users,
        "response": response_details,
        "attackDetails": attack_details,
        "modelInformation": model_information,
        "externalReferences": external_refs if external_refs else None
    }
    
    return mitre_report


if __name__ == "__main__":
    ai_flaw_example = "/Users/elainezhu/Downloads/ai_flaw_report_67120781-6f5a-4bdf-973b-e2355161a7bd.json"
    mitre_report = convert_to_mitre_atlas(ai_flaw_example)
    print(json.dumps(mitre_report, indent=4))