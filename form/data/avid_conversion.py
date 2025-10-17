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

def _collect_system_info(data: dict):
    """
    Returns (product_name, product_version, vendor_name, all_systems).
    """
    product_name = "Unknown System"
    product_version = ""
    vendor_name = "Unknown"
    all_systems = []

    if "Systems" in data and isinstance(data["Systems"], list) and data["Systems"]:
        all_systems = data["Systems"]
        product_name = all_systems[0]

    return product_name, product_version, vendor_name, all_systems

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

def _get_from_nested(data: dict, path: list, default=None):
    cur = data
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur

def _map_system_to_vendor(system_name: str) -> dict:
    """Maps AI system names to their developers/deployers."""
    vendor_mapping = {
        "GPT-3.5-Turbo": {"developer": "OpenAI", "deployer": "OpenAI"},
        "GPT-4": {"developer": "OpenAI", "deployer": "OpenAI"},
        "GPT-4o": {"developer": "OpenAI", "deployer": "OpenAI"},
        "Claude": {"developer": "Anthropic", "deployer": "Anthropic"},
        "Claude 3": {"developer": "Anthropic", "deployer": "Anthropic"},
        "Claude 3.5": {"developer": "Anthropic", "deployer": "Anthropic"},
        "Gemini": {"developer": "Google", "deployer": "Google"},
        "PaLM": {"developer": "Google", "deployer": "Google"},
        "LLaMA": {"developer": "Meta", "deployer": "Meta"},
        "Llama": {"developer": "Meta", "deployer": "Meta"},
        "Copilot": {"developer": "Microsoft", "deployer": "Microsoft"},
        "DALL-E": {"developer": "OpenAI", "deployer": "OpenAI"},
        "DALL-E 2": {"developer": "OpenAI", "deployer": "OpenAI"},
        "DALL-E 3": {"developer": "OpenAI", "deployer": "OpenAI"},
        "Midjourney": {"developer": "Midjourney Inc", "deployer": "Midjourney Inc"},
        "Stable Diffusion": {"developer": "Stability AI", "deployer": "Stability AI"},
        "BERT": {"developer": "Google", "deployer": "HuggingFace"},
        "bert-base-uncased": {"developer": "Google", "deployer": "HuggingFace"}
    }
    return vendor_mapping.get(system_name, {"developer": "Unknown", "deployer": "Unknown"})

def convert_to_avid_format(raw_or_path) -> dict:
    """
    Converts AI flaw report (raw form JSON) into AVID format.
    Accepts dict, path to JSON file, or JSON string.
    """
    data = _load_any(raw_or_path)

    product_name, product_version, vendor_name, all_systems = _collect_system_info(data)

    # artifacts, developers, and deployers lists
    artifacts = []
    developers = set()
    deployers = set()

    for system in all_systems:
        artifacts.append({
            "type": "Model",
            "name": system
        })
        vendor_info = _map_system_to_vendor(system)
        developers.add(vendor_info["developer"])
        deployers.add(vendor_info["deployer"])

    if not artifacts:
        artifacts.append({"type": "Model", "name": product_name})
        if vendor_name and vendor_name != "Unknown":
            developers.add(vendor_name)
            deployers.add(vendor_name)

    report_id = _get_str(data, "Report ID", "identifier", default=None)
    if not report_id:
        atid = data.get("@id", "")
        if isinstance(atid, str) and atid.rsplit("/", 1)[-1]:
            report_id = atid.rsplit("/", 1)[-1]
        else:
            report_id = f"TEMP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    year = datetime.now().year
    avid_report_id = f"AVID-{year}-R{report_id[:4].upper()}" if len(report_id) >= 4 else f"AVID-{year}-RXXXX"

    report_types = _get_list(data, "Report Types", "reportType")
    impacts = _get_list(data, "Impacts", "impacts")
    specific_harms = _get_list(data, "Specific Harm Types", "aifr:specificHarmTypes")

    classof = "LLM Evaluation"
    if "Security Incident Report" in report_types or "Malign Actor" in report_types:
        classof = "Security"
    elif "Real-World Incidents" in report_types:
        classof = "Incident"
    elif "Vulnerability Report" in report_types:
        classof = "Vulnerability"
    elif "Hazard Report" in report_types:
        classof = "Safety"

    problem_type = "Detection"
    if "Security Incident Report" in report_types:
        problem_type = "Adversarial Attack"
    elif "Discrimination/Bias" in impacts:
        problem_type = "Bias"
    elif "Privacy" in impacts:
        problem_type = "Privacy Violation"
    elif "Misinformation" in impacts:
        problem_type = "Misinformation"


    # description
    description = _get_str(
        data,
        "Flaw Description",
        "Incident Description",
        "Incident Description - Detailed",
        "Flaw Description - Detailed",
        "description",
        default="No description provided"
    )
   
    description = description.replace("**Detailed Description:**\n", "").strip()


    # problem description
    problem_description = description
    if specific_harms:
        harm_list = ", ".join(specific_harms[:2])
        problem_description = f"{description}. Specific harms: {harm_list}"

    # Map impacts to AVID risk domains and SEP view (I used Claude for this one as I'm unsure about AVID risk domains)
    risk_domains = []
    sep_views = []

    impact_to_risk_mapping = {
        "Discrimination/Bias": {
            "domain": "Ethics",
            "sep": ["E0101: Group fairness", "E0102: Individual fairness"]
        },
        "Privacy": {
            "domain": "Privacy",
            "sep": ["P0201: Sensitive data", "P0202: Right to be forgotten"]
        },
        "Misinformation": {
            "domain": "Ethics",
            "sep": ["E0301: Toxicity", "E0302: Misinformation"]
        },
        "Safety": {
            "domain": "Safety",
            "sep": ["S0403: Dangerous action"]
        },
        "Security": {
            "domain": "Security",
            "sep": ["S0100: Software security"]
        },
        "Environmental": {
            "domain": "Ethics",
            "sep": ["E0401: Environmental"]
        }
    }

    for impact in impacts:
        mapping = impact_to_risk_mapping.get(impact)
        if mapping:
            if mapping["domain"] not in risk_domains:
                risk_domains.append(mapping["domain"])
            sep_views.extend(mapping["sep"])

    if not risk_domains:
        risk_domains = ["Ethics"]
        sep_views = ["E0100: Bias"]

    # also Claude for this one
    lifecycle_view = ["L05: Evaluation"]
    if "Real-World Incidents" in report_types:
        lifecycle_view = ["L06: Deployment"]
    elif "Vulnerability Report" in report_types:
        lifecycle_view = ["L04: Verification"]


    # metrics
    metrics = []
    detection_methods = _get_list(data, "Detection", "aifr:detectionMethods")
    severity = _get_str(data, "Severity", "severity", default="Unknown")
    prevalence = _get_str(data, "Prevalence", "prevalence", default="Unknown")

    if detection_methods:
        for method in detection_methods:
            metric = {
                "name": method,
                "features": {
                    "measured": f"Severity: {severity}, Prevalence: {prevalence}"
                }
            }

            if "Discrimination/Bias" in impacts:
                stakeholders = _get_list(data, "Impacted Stakeholder(s)", "aifr:impactedStakeholders")
                if stakeholders:
                    metric["features"]["sensitive"] = ", ".join(stakeholders)

            if "observation" in method.lower():
                metric["detection_method"] = {
                    "type": "Manual Review",
                    "name": "User-reported observation"
                }
            elif "automated" in method.lower() or "testing" in method.lower():
                metric["detection_method"] = {
                    "type": "Automated Test",
                    "name": "Automated vulnerability scan"
                }

            metrics.append(metric)


    # references
    references = []

    poc = _get_str(data, "Proof-of-Concept Exploit", default="")
    if not poc:
        poc = _get_from_nested(data, ["aifr:vulnerability", "aifr:proofOfConcept"], default="")
   
    if poc:
        references.append({
            "type": "source",
            "label": "Proof of Concept",
            "url": ""
        })

    context_info = _get_str(data, "Context Info", "aifr:contextInfo", default="")
    if context_info:
        references.append({
            "type": "misc",
            "label": "Additional Context",
            "url": ""
        })


    # credit
    credit = []
    reporter_id = _get_str(data, "Reporter ID", default="")
   
    if reporter_id:
        credit.append({
            "lang": "eng",
            "value": f"Reporter: {reporter_id}"
        })

    submitter_rel = _get_str(data, "Submitter Relationship", default="")
    if submitter_rel:
        credit.append({
            "lang": "eng",
            "value": f"Relationship: {submitter_rel}"
        })

    if not credit:
        credit.append({"lang": "eng", "value": "Anonymous"})

    submission_timestamp = _get_str(data, "Submission Timestamp", "dateCreated", default="")
    flaw_timestamp = _get_str(data, "Flaw Timestamp Start", default="")

    reported_date = None
    if submission_timestamp:
        try:
            dt = datetime.fromisoformat(submission_timestamp.replace('Z', '+00:00'))
            reported_date = dt.strftime('%Y-%m-%d')
        except:
            pass
    elif flaw_timestamp:
        reported_date = flaw_timestamp[:10] if len(flaw_timestamp) >= 10 else flaw_timestamp

    if not reported_date:
        reported_date = datetime.now().strftime('%Y-%m-%d')


    # AVID report
    avid_report = {
        "data_type": "AVID",
        "data_version": "0.1",
        "metadata": {
            "report_id": avid_report_id
        },
        "affects": {
            "developer": list(developers) if developers else [],
            "deployer": list(deployers) if deployers else [],
            "artifacts": artifacts
        },
        "problemtype": {
            "classof": classof,
            "type": problem_type,
            "description": {
                "lang": "eng",
                "value": problem_description[:500]
            }
        },
        "metrics": metrics,
        "references": references,
        "description": {
            "lang": "eng",
            "value": description[:1000]
        },
        "impact": {
            "avid": {
                "risk_domain": risk_domains,
                "sep_view": sep_views,
                "lifecycle_view": lifecycle_view,
                "taxonomy_version": "0.1"
            }
        },
        "credit": credit,
        "reported_date": reported_date
    }

    if "Vulnerability Report" in report_types:
        vuln_id = f"AVID-{year}-V{report_id[:3].upper()}" if len(report_id) >= 3 else f"AVID-{year}-VXXX"
        avid_report["impact"]["avid"]["vuln_id"] = vuln_id

    return avid_report


if __name__ == "__main__":
    ai_flaw_example = "INSERT_FILE_PATH"
    avid_report = convert_to_avid_format(ai_flaw_example)
    print(json.dumps(avid_report, indent=4))