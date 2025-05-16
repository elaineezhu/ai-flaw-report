from datetime import datetime

def generate_machine_readable_output(form_data):
    """Generate machine-readable JSON-LD output"""
    json_ld = {
        "@context": "https://schema.org",
        "@type": "AIFlawReport",
        "reportId": form_data.get("Report ID"),
        "dateCreated": datetime.now().isoformat(),
        "reportStatus": form_data.get("Report Status"),
        "reportTypes": form_data.get("Report Types", []),
        "basicInformation": {
            "reporterId": form_data.get("Reporter ID"),
            "sessionId": form_data.get("Session ID"),
            "flawTimestampStart": form_data.get("Flaw Timestamp Start"),
            "flawTimestampEnd": form_data.get("Flaw Timestamp End"),
            "systems": form_data.get("Systems", [])
        },
        "commonFields": {
            "contextInfo": form_data.get("Context Info"),
            "flawDescription": form_data.get("Flaw Description"),
            "policyViolation": form_data.get("Policy Violation"),
            "severity": form_data.get("Severity"),
            "prevalence": form_data.get("Prevalence"),
            "impacts": form_data.get("Impacts", []),
            "impactedStakeholders": form_data.get("Impacted Stakeholder(s)", []),
            "riskSource": form_data.get("Risk Source", []),
            "bountyEligibility": form_data.get("Bounty Eligibility")
        },
        "disclosurePlan": {
            "disclosureIntent": form_data.get("Disclosure Intent"),
            "disclosureTimeline": form_data.get("Disclosure Timeline"),
            "disclosureChannels": form_data.get("Disclosure Channels", []),
            "embargoRequest": form_data.get("Embargo Request")
        }
    }
    
    # Report-type specific sections
    if "Real-World Events" in form_data.get("Report Types", []):
        json_ld["realWorldEvent"] = {
            "incidentDescription": form_data.get("Description of the Incident(s)"),
            "implicatedSystems": form_data.get("Implicated Systems"),
            "submitterRelationship": form_data.get("Submitter Relationship"),
            "eventDates": form_data.get("Event Date(s)"),
            "eventLocations": form_data.get("Event Location(s)"),
            "experiencedHarmTypes": form_data.get("Experienced Harm Types", []),
            "experiencedHarmSeverity": form_data.get("Experienced Harm Severity"),
            "harmNarrative": form_data.get("Harm Narrative")
        }
    
    if "Malign Actor" in form_data.get("Report Types", []):
        json_ld["malignActor"] = {
            "tactics": form_data.get("Tactic Select", []),
            "impact": form_data.get("Impact", [])
        }
    
    if "Security Incident Report" in form_data.get("Report Types", []):
        json_ld["securityIncident"] = {
            "threatActorIntent": form_data.get("Threat Actor Intent"),
            "detection": form_data.get("Detection", [])
        }
    
    if "Vulnerability Report" in form_data.get("Report Types", []):
        json_ld["vulnerability"] = {
            "proofOfConcept": form_data.get("Proof-of-Concept Exploit")
        }
    
    if "Hazard Report" in form_data.get("Report Types", []):
        json_ld["hazard"] = {
            "examples": form_data.get("Examples"),
            "replicationPacket": form_data.get("Replication Packet"),
            "statisticalArgument": form_data.get("Statistical Argument")
        }
    
    return json_ld