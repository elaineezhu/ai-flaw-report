import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field, validator
import pyld
from pyld import jsonld

class UnknownAISystem(BaseModel):
    """Schema for unknown AI systems described by users."""
    description: str = Field(..., min_length=1, description="User description of unknown AI system")

class RawAIFlawReport(BaseModel):
    """Raw form input - matches actual complete form structure"""
    
    class Config:
        extra = "allow"
        populate_by_name = True
    
    report_id: Optional[str] = Field(None, alias="Report ID")
    reporter_id: Optional[str] = Field(None, alias="Reporter ID")
    session_id: Optional[str] = Field(None, alias="Session ID")
    systems: Optional[List[str]] = Field(default=[], alias="Systems")
    flaw_timestamp_start: Optional[str] = Field(None, alias="Flaw Timestamp Start")
    submission_timestamp: Optional[str] = Field(None, alias="Submission Timestamp")
    
    report_types: List[str] = Field(default=[], alias="Report Types")
    
    flaw_description: Optional[str] = Field(None, alias="Flaw Description")
    incident_description: Optional[str] = Field(None, alias="Incident Description")
    incident_description_detailed: Optional[str] = Field(None, alias="Incident Description - Detailed")
    flaw_description_detailed: Optional[str] = Field(None, alias="Flaw Description - Detailed")
    
    policy_violation: Optional[str] = Field(None, alias="Policy Violation")
    potential_policy_violation: Optional[str] = Field(None, alias="Potential Policy Violation")
    severity: Optional[str] = Field(None, alias="Severity")
    prevalence: Optional[str] = Field(None, alias="Prevalence")
    
    impacts: Optional[List[str]] = Field(default=[], alias="Impacts")
    impacts_other: Optional[str] = Field(None, alias="Impacts_Other")
    specific_harm_types: Optional[List[str]] = Field(default=[], alias="Specific Harm Types")
    impacted_stakeholders: Optional[List[str]] = Field(default=[], alias="Impacted Stakeholder(s)")
    csam_related: Optional[str] = Field(None, alias="CSAM Related")
    
    risk_sources: Optional[Dict[str, Any]] = Field(None, alias="Risk Source(s)")
    
    context_info: Optional[str] = Field(None, alias="Context Info")
    proof_of_concept: Optional[str] = Field(None, alias="Proof-of-Concept Exploit")
    
    submitter_relationship: Optional[str] = Field(None, alias="Submitter Relationship")
    submitter_relationship_other: Optional[str] = Field(None, alias="Submitter_Relationship_Other")
    incident_locations: Optional[str] = Field(None, alias="Incident Location(s)")
    harm_narrative: Optional[str] = Field(None, alias="Harm Narrative")
    
    attacker_resources: Optional[List[str]] = Field(default=[], alias="Attacker Resources")
    attacker_objectives: Optional[List[str]] = Field(default=[], alias="Attacker Objectives")
    objective_context: Optional[str] = Field(None, alias="Objective Context")
    detection_methods: Optional[List[str]] = Field(default=[], alias="Detection")
    
    statistical_argument: Optional[str] = Field(None, alias="Statistical Argument with Examples")
    
    disclosure_intent: str = Field(..., alias="Disclosure Intent")
    disclosure_timeline: Optional[str] = Field(None, alias="Disclosure Timeline")
    disclosure_channels: Optional[List[str]] = Field(default=[], alias="Disclosure Channels")
    disclosure_channels_other: Optional[str] = Field(None, alias="Disclosure_Channels_Other")
    embargo_request: Optional[str] = Field(None, alias="Embargo Request")
    
    @validator('disclosure_intent')
    def validate_disclosure_intent(cls, v):
        valid_intents = {'Yes', 'No', 'Undecided', 'Already Public Knowledge'}
        if v not in valid_intents:
            raise ValueError(f'Disclosure intent must be one of: {valid_intents}')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        if v is None:
            return v
        valid_severities = {
            'Negligible', 'Low', 'Medium', 'High', 'Critical', 'Significant'
        }
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {valid_severities}')
        return v

class AISystem(BaseModel):
    """Enriched AI System information"""
    
    id: str = Field(..., description="System identifier/URL")
    name: str = Field(..., description="System name")
    version: str = Field(..., description="System version")
    slug: str = Field(..., description="Internal slug for lookups")
    display_name: str = Field(..., description="Human-friendly display name")
    system_type: str = Field(default="known", description="'known' or 'unknown'")
    description: Optional[str] = Field(None, description="For unknown systems")
    publisher_info: Optional[Dict[str, Any]] = Field(None, description="Publisher/organization data")

class ProcessedAIFlawReport(BaseModel):
    """Fully processed flaw report with enriched data - fields ordered to match form flow"""
    
    # Basic Information
    reporter_id: Optional[str] = None
    report_id: str = Field(..., description="Generated report ID")
    session_id: Optional[str] = None
    ai_systems: List[AISystem] = Field(..., description="Fully enriched system data")
    flaw_timestamp_start: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Core Description
    flaw_description: str
    policy_violation: str
    
    # Risks and Impact
    prevalence: str
    severity: str
    impacts: List[str] = Field(default=[])
    specific_harm_types: List[str] = Field(default=[])
    impacted_stakeholders: List[str] = Field(default=[])
    
    # Report Classification
    report_types: List[str] = Field(default=[])
    
    # Conditional Sections
    incident_data: Optional[Dict[str, Any]] = None
    security_data: Optional[Dict[str, Any]] = None
    vulnerability_data: Optional[Dict[str, Any]] = None
    hazard_data: Optional[Dict[str, Any]] = None

    # Disclosure Information
    disclosure_intent: str
    disclosure_timeline: Optional[str] = None
    disclosure_channels: List[str] = Field(default=[])

    # Raw data storage
    raw_data: Optional[Dict[str, Any]] = Field(default=None, repr=False)


def process_raw_report(raw_data: Dict[str, Any]) -> ProcessedAIFlawReport:
    """Convert raw form data to processed report by resolving AI systems"""
    
    raw_report = RawAIFlawReport.model_validate(raw_data)
    kb = AIFlawKnowledgeBase()
    
    report_id = raw_data.get("Report ID") or f"AFL-{hashlib.md5(json.dumps(raw_data, sort_keys=True).encode()).hexdigest()[:8]}"
    
    ai_systems = []
    systems_list = raw_report.systems or []
    for system_name in systems_list:
        system_data = kb.find_system_by_name_or_slug(system_name)
        if system_data:
            internal_data = system_data.get("_aifr_internal", {})
            ai_system = AISystem(
                id=system_data.get("@id", f"https://aiflawreports.org/systems/{system_name}"),
                name=system_data.get("name", system_name),
                version=system_data.get("version", ""),
                slug=internal_data.get("slug", system_name),
                display_name=internal_data.get("displayName", system_name),
                system_type="known"
            )
        else:
            ai_system = AISystem(
                id=f"https://aiflawreports.org/systems/{system_name.replace(' ', '_')}",
                name=system_name,
                version="",
                slug=system_name,
                display_name=system_name,
                system_type="partially_known"
            )
        ai_systems.append(ai_system)
    
    if not ai_systems:
        ai_systems.append(AISystem(
            id=f"https://aiflawreports.org/reports/{report_id}/unknown-system",
            name="Unknown System",
            version="",
            slug="",
            display_name="Unknown System",
            system_type="unknown",
            description="No specific system identified"
        ))
    
    if raw_report.incident_description:
        description = raw_report.incident_description
    elif raw_report.incident_description_detailed:
        description = f"**Detailed Description:**\n{raw_report.incident_description_detailed}"
    elif raw_report.flaw_description:
        description = raw_report.flaw_description
    elif raw_report.flaw_description_detailed:
        description = f"**Detailed Description:**\n{raw_report.flaw_description_detailed}"
    else:
        description = "No description provided"
    
    policy_violation = raw_report.policy_violation or raw_report.potential_policy_violation or "Not specified"
    
    incident_data = None
    if "Real-World Incidents" in raw_report.report_types:
        incident_data = {
            "description": raw_report.incident_description,
            "detailed_description": raw_report.incident_description_detailed,
            "locations": raw_report.incident_locations,
            "harm_narrative": raw_report.harm_narrative,
            "submitter_relationship": raw_report.submitter_relationship,
            "submitter_relationship_other": raw_report.submitter_relationship_other
        }
    
    security_data = None
    if any(rt in raw_report.report_types for rt in ["Malign Actor", "Security Incident Report"]):
        security_data = {
            "attacker_resources": raw_report.attacker_resources or [],
            "attacker_objectives": raw_report.attacker_objectives or [],
            "objective_context": raw_report.objective_context,
            "detection_methods": raw_report.detection_methods or []
        }
    
    vulnerability_data = None
    if "Vulnerability Report" in raw_report.report_types:
        vulnerability_data = {
            "proof_of_concept": raw_report.proof_of_concept
        }
    
    hazard_data = None
    if "Hazard Report" in raw_report.report_types:
        hazard_data = {
            "statistical_argument": raw_report.statistical_argument
        }
    
    processed_report = ProcessedAIFlawReport(
        reporter_id=raw_report.reporter_id,
        report_id=report_id,
        session_id=raw_report.session_id,
        ai_systems=ai_systems,
        flaw_timestamp_start=raw_report.flaw_timestamp_start,
        flaw_description=description,
        policy_violation=policy_violation,
        prevalence=raw_report.prevalence or "Unknown",
        severity=raw_report.severity or "Unknown",
        impacts=raw_report.impacts or [],
        specific_harm_types=raw_report.specific_harm_types or [],
        impacted_stakeholders=raw_report.impacted_stakeholders or [],
        report_types=raw_report.report_types,
        incident_data=incident_data,
        security_data=security_data,
        vulnerability_data=vulnerability_data,
        hazard_data=hazard_data,
        disclosure_intent=raw_report.disclosure_intent,
        disclosure_timeline=raw_report.disclosure_timeline,
        disclosure_channels=raw_report.disclosure_channels or []
    )
    
    processed_report.raw_data = raw_data
    return processed_report


def clean_internal_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove fields starting with underscore for clean JSON-LD output."""
    if isinstance(data, dict):
        return {k: clean_internal_fields(v) for k, v in data.items() if not k.startswith("_")}
    elif isinstance(data, list):
        return [clean_internal_fields(item) for item in data]
    else:
        return data

class AIFlawKnowledgeBase:
    """Knowledge base for AI systems and organizations"""
    
    def __init__(self, kb_path: str = "knowledge-base"):
        self.kb_path = Path(kb_path)
        self.systems_data = None
        self.organizations_data = None
        self.slug_map = {}
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load knowledge base files or create minimal fallback data"""
        try:
            if (self.kb_path / "ai-systems.jsonld").exists():
                with open(self.kb_path / "ai-systems.jsonld") as f:
                    self.systems_data = json.load(f)
            else:
                self.systems_data = {"@graph": []}
                
            if (self.kb_path / "organizations.jsonld").exists():
                with open(self.kb_path / "organizations.jsonld") as f:
                    self.organizations_data = json.load(f)
            else:
                self.organizations_data = {"@graph": []}
                
        except (FileNotFoundError, json.JSONDecodeError):
            self.systems_data = {"@graph": []}
            self.organizations_data = {"@graph": []}
        
        self._build_slug_map()
        
    
    def _build_slug_map(self):
        """Build slug to system/org mapping"""
        self.slug_map = {}
        
        if self.systems_data:
            for system in self.systems_data.get("@graph", []):
                slug = system.get("_aifr_internal", {}).get("slug")
                if slug:
                    self.slug_map[slug] = system
        
        if self.organizations_data:
            for org in self.organizations_data.get("@graph", []):
                slug = org.get("_aifr_internal", {}).get("slug")
                if slug:
                    self.slug_map[slug] = org
    
    def find_system_by_name_or_slug(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Find system by name or slug with fuzzy matching"""
        # Direct slug match
        if identifier in self.slug_map:
            return self.slug_map[identifier]
        
        # Search by name (case-insensitive partial match)
        identifier_lower = identifier.lower()
        for system in self.systems_data.get("@graph", []):
            name = system.get("name", "").lower()
            display_name = system.get("_aifr_internal", {}).get("displayName", "").lower()
            
            if (identifier_lower in name or 
                identifier_lower in display_name or
                name in identifier_lower or
                display_name in identifier_lower):
                return system
        
        return None
    
    def find_organization_by_id(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Find organization by @id URI"""
        for org in self.organizations_data.get("@graph", []):
            if org.get("@id") == org_id:
                return org
        return None
    
    def get_system_jsonld(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get clean JSON-LD representation of system with full publisher data"""
        system = self.find_system_by_name_or_slug(identifier)
        if not system:
            return None
        
        jsonld_system = clean_internal_fields(system)
        
        if "@type" not in jsonld_system:
            jsonld_system["@type"] = "schema:SoftwareApplication"
        
        publisher_id = system.get("publisher", {}).get("@id")
        if publisher_id:
            org_data = self.find_organization_by_id(publisher_id)
            if org_data:
                publisher_jsonld = clean_internal_fields(org_data)
                if "@type" not in publisher_jsonld:
                    publisher_jsonld["@type"] = "schema:Organization"
                jsonld_system["publisher"] = publisher_jsonld
        
        return jsonld_system

def _normalized_description(text: Optional[str]) -> str:
    if not text:
        return "No description provided"
    prefix = "**Detailed Description:**"
    t = text.lstrip()
    if t.startswith(prefix):
        t = t[len(prefix):].lstrip()
    return t

def serialize_to_jsonld(processed_report: ProcessedAIFlawReport) -> Dict[str, Any]:
    kb = AIFlawKnowledgeBase()

    jsonld_systems, system_names = [], []
    for system in processed_report.ai_systems:
        if system.system_type == "unknown":
            jsonld_systems.append({
                "@type": "schema:SoftwareApplication",
                "@id": system.id,
                "name": "Unknown System",
                "description": system.description
            })
            system_names.append("Unknown System")
        else:
            js = kb.get_system_jsonld(system.slug or system.name)
            if js:
                jsonld_systems.append(js)
                system_names.append(system.display_name)
            else:
                jsonld_systems.append({
                    "@type": "schema:SoftwareApplication",
                    "@id": system.id,
                    "name": system.name,
                    "version": system.version
                })
                system_names.append(system.display_name)

    jsonld_report = {
        "@context": [
            "https://schema.org/",
            {
                "aifr": "https://aiflawreports.org/schema/",
                "aiSystem": "aifr:aiSystem",
                "severity": "aifr:severity",
                "prevalence": "aifr:prevalence",
                "impacts": "aifr:impacts",
                "reportType": "aifr:reportType",
                "riskSource": "aifr:riskSource",
                "contextInfo": "aifr:contextInfo"
            }
        ],
        "@type": "aifr:AIFlawReport",
        "@id": f"https://aiflawreports.org/reports/{processed_report.report_id}",
        "name": f"AI Flaw Report: {', '.join(system_names)}",
        "description": _normalized_description(processed_report.flaw_description),
        "aiSystem": jsonld_systems,
        "severity": processed_report.severity,
        "prevalence": processed_report.prevalence,
        "impacts": processed_report.impacts,
        "reportType": processed_report.report_types,
        "dateCreated": processed_report.created_at.isoformat(),
        "identifier": processed_report.report_id,
        "aifr:policyViolation": processed_report.policy_violation,
    }

    if processed_report.reporter_id:
        jsonld_report["author"] = {"@type": "schema:Person", "identifier": processed_report.reporter_id}
    if processed_report.session_id:
        jsonld_report["aifr:sessionId"] = processed_report.session_id
    if processed_report.flaw_timestamp_start:
        jsonld_report["aifr:flawTimestamp"] = processed_report.flaw_timestamp_start
    if processed_report.impacted_stakeholders:
        jsonld_report["aifr:impactedStakeholders"] = processed_report.impacted_stakeholders
    if processed_report.specific_harm_types:
        jsonld_report["aifr:specificHarmTypes"] = processed_report.specific_harm_types
    if processed_report.incident_data:
        inc = {
            "@type": "aifr:RealWorldIncident",
            "description": processed_report.incident_data.get("description"),
            "location": processed_report.incident_data.get("locations"),
            "aifr:harmNarrative": processed_report.incident_data.get("harm_narrative"),
        }
        if processed_report.incident_data.get("submitter_relationship"):
            inc["aifr:submitterRelationship"] = processed_report.incident_data["submitter_relationship"]
        jsonld_report["aifr:incident"] = inc
    if processed_report.security_data:
        sec = {
            "@type": "aifr:SecurityIncident",
            "aifr:attackerResources": processed_report.security_data.get("attacker_resources", []),
            "aifr:attackerObjectives": processed_report.security_data.get("attacker_objectives", []),
            "aifr:detectionMethods": processed_report.security_data.get("detection_methods", [])
        }
        if processed_report.security_data.get("objective_context"):
            sec["aifr:objectiveContext"] = processed_report.security_data["objective_context"]
        jsonld_report["aifr:securityAspect"] = sec
    if processed_report.vulnerability_data:
        jsonld_report["aifr:vulnerability"] = {
            "@type": "aifr:Vulnerability",
            "aifr:proofOfConcept": processed_report.vulnerability_data.get("proof_of_concept")
        }
    if processed_report.hazard_data:
        jsonld_report["aifr:hazard"] = {
            "@type": "aifr:Hazard",
            "aifr:statisticalArgument": processed_report.hazard_data.get("statistical_argument")
        }

    disclosure = {"@type": "aifr:DisclosurePlan", "aifr:intent": processed_report.disclosure_intent}
    if processed_report.disclosure_timeline:
        disclosure["aifr:timeline"] = processed_report.disclosure_timeline
    if processed_report.disclosure_channels:
        disclosure["aifr:channels"] = processed_report.disclosure_channels
    jsonld_report["aifr:disclosure"] = disclosure

    if getattr(processed_report, "raw_data", None):
        rd = processed_report.raw_data
        jsonld_report["aifr:raw"] = rd

        # Map Risk Source(s) -> aifr:riskSource
        rs = rd.get("Risk Source(s)")
        if rs:
            jsonld_report["aifr:riskSource"] = {
                "@type": "aifr:RiskSourceAnalysis",
                "aifr:responsibleFactors": rs.get("Responsible Factors", []),
                "aifr:responsibleFactorsSubcategories": rs.get("Responsible Factors Subcategories", {}),
                "aifr:responsibleFactorsContext": rs.get("Responsible Factors Context", "")
            }

        # Map Context Info -> aifr:contextInfo
        if "Context Info" in rd and rd["Context Info"] not in (None, ""):
            jsonld_report["aifr:contextInfo"] = rd["Context Info"]

        # Map Submission Timestamp -> aifr:submissionTimestamp
        if "Submission Timestamp" in rd and rd["Submission Timestamp"]:
            jsonld_report["aifr:submissionTimestamp"] = rd["Submission Timestamp"]

        if "Embargo Request" in rd and rd["Embargo Request"]:
            jsonld_report["aifr:disclosure"]["aifr:embargoRequest"] = rd["Embargo Request"]

    return jsonld_report



def generate_machine_readable_output(form_data: Dict[str, Any]) -> str:
    """
    Main function to replace the original manual JSON-LD generation
    Uses Pydantic validation, knowledge base enrichment, and proper JSON-LD structure
    """
    try:
        processed_report = process_raw_report(form_data)
        
        jsonld_report = serialize_to_jsonld(processed_report)
        
        try:
            compacted = jsonld.compact(jsonld_report, jsonld_report["@context"])
            return json.dumps(compacted, indent=2)
        except Exception:
            return json.dumps(jsonld_report, indent=2)
            
    except Exception as e:
        return json.dumps({
            "@context": "https://schema.org/",
            "@type": "Report",
            "@id": f"https://aiflawreports.org/reports/{form_data.get('Report ID', 'unknown')}",
            "name": "AI Flaw Report",
            "description": form_data.get("Flaw Description", ""),
            "dateCreated": datetime.now(timezone.utc).isoformat(),
            "aifr:processingError": str(e)
        }, indent=2)

def validate_jsonld_output(jsonld_string: str) -> tuple[bool, Optional[str]]:
    """
    Validate the generated JSON-LD
    Returns (is_valid, error_message)
    """
    try:
        data = json.loads(jsonld_string)
        
        if "@context" not in data:
            return False, "Missing @context"
        if "@type" not in data:
            return False, "Missing @type"
        if "@id" not in data:
            return False, "Missing @id"
        
        try:
            expanded = jsonld.expand(data)
            return True, None
        except Exception as e:
            return False, f"JSON-LD expansion error: {e}"
            
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def update_storage_interface_for_jsonld(form_data: Dict[str, Any]):
    """
    Enhanced storage function that generates both formats
    Can be integrated into existing storage providers
    """
    jsonld_output = generate_machine_readable_output(form_data)
    
    is_valid, error = validate_jsonld_output(jsonld_output)
    
    if not is_valid:
        print(f"JSON-LD validation warning: {error}")
    
    return {
        "form_data": form_data,
        "jsonld": json.loads(jsonld_output),
        "jsonld_string": jsonld_output,
        "validation_status": is_valid,
        "validation_error": error
    }