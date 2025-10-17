import json
from pathlib import Path
from datetime import datetime, timezone

def _load_any(obj):
    """
    Accept dict, path to JSON file, or JSON string.
    Return a Python dict.
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
    Returns (product_name, product_version, vendor_name).
    Handles both raw and JSON-LD shapes.
    """
    # Defaults
    product_name = "Unknown System"
    product_version = ""
    vendor_name = "AI Flaw Reporting"

    # RAW (form) shape: "Systems": ["GPT-3.5-Turbo", ...]
    if "Systems" in data and isinstance(data["Systems"], list) and data["Systems"]:
        product_name = data["Systems"][0]

    # JSON-LD shape: "aiSystem": [{ "name": "...", "version": "...", "publisher": {...}}]
    elif "aiSystem" in data:
        sys0 = _first(data.get("aiSystem", []), {})
        if isinstance(sys0, dict):
            product_name = sys0.get("name", product_name)
            product_version = sys0.get("version", product_version)
            pub = sys0.get("publisher") or sys0.get("schema:publisher")
            if isinstance(pub, dict):
                vendor_name = pub.get("name", vendor_name)

    return product_name, product_version, vendor_name

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

def _string_bool(val, truthy={"yes", "true", "1"}):
    """
    Convert various inputs to 'True'/'False' strings (CERT fields use string booleans).
    """
    if isinstance(val, bool):
        return "True" if val else "False"
    if isinstance(val, str):
        return "True" if val.strip().lower() in truthy else "False"
    return "False"

def convert_to_cert_json(raw_or_path) -> dict:
    """
    Convert AI flaw report (raw form JSON or JSON-LD) into CERT VRF-like JSON format.
    Accepts dict, path to JSON file, or JSON string.
    """
    data = _load_any(raw_or_path)

    product_name, product_version, vendor_name = _collect_system_info(data)

    vul_description = _get_str(
        data,
        "Flaw Description",
        "Incident Description",
        "Incident Description - Detailed",
        "Flaw Description - Detailed",
        default=data.get("description", "")
    )

    vul_exploit = _get_str(data, "Proof-of-Concept Exploit", default="")
    if not vul_exploit:
        vul_exploit = _get_from_nested(
            data, ["aifr:vulnerability", "aifr:proofOfConcept"], default=""
        )

    impacts_list = _get_list(data, "Impacts", "impacts")
    vul_impact = ", ".join(impacts_list) if impacts_list else ""

    # Discovery context
    vul_discovery = _get_str(data, "Context Info", default=data.get("aifr:contextInfo", ""))

    # Disclosure intent & timeline
    disclosure_intent = (
        _get_str(data, "Disclosure Intent", default=None)
        or _get_from_nested(data, ["aifr:disclosure", "aifr:intent"], default="")
    )
    disclosure_timeline = (
        _get_str(data, "Disclosure Timeline", default=None)
        or _get_from_nested(data, ["aifr:disclosure", "aifr:timeline"], default="")
    )

    # Submission meta
    report_id = _get_str(data, "Report ID", "identifier", default=None)
    submitted = _get_str(
        data,
        "Submission Timestamp",
        "dateCreated",
        default=datetime.now(timezone.utc).isoformat()
    )
    reporter_id = _get_str(data, "Reporter ID", default="")
    if not report_id:
        # JSON-LD often puts it in @id like "https://.../reports/<id>"
        atid = data.get("@id", "")
        if isinstance(atid, str) and atid.rsplit("/", 1)[-1]:
            report_id = atid.rsplit("/", 1)[-1]
        else:
            report_id = f"VRF-{datetime.now(timezone.utc).strftime('%y-%m-%d-%H%M%S')}"

    submitted = _get_str(
        data,
        "Submission Timestamp",
        "dateCreated",
        default=datetime.now(timezone.utc).isoformat()
    )

    report_types = _get_list(data, "Report Types", "reportType")
    submission_type = _first(report_types, "Vulnerability Report")

    title = f"[VRF#{report_id}] {product_name}"

    cert_json = {
        'contact_name': reporter_id,
        'contact_org': '',
        'contact_email': '',
        'contact_phone': '',
        'share_release': 'False',
        'credit_release': 'False',
        'coord_status': [],

        'vendor_name': vendor_name or 'Central Services',
        'multiplevendors': 'False',
        'other_vendors': '',
        'first_contact': None,
        'vendor_communication': '',

        'product_name': product_name,
        'product_version': product_version or '',

        'ics_impact': False,
        'metadata': {'ai_ml_system': True}, 
        'vul_description': vul_description,
        'vul_exploit': vul_exploit,
        'vul_impact': vul_impact,
        'vul_discovery': vul_discovery,
        'vul_public': 'False',
        'public_references': '',
        'vul_exploited': 'False',
        'exploit_references': '',
        'vul_disclose': _string_bool(disclosure_intent),
        'disclosure_plans': disclosure_timeline or '',
        'tracking': '',
        'comments': _get_str(data, "Harm Narrative", default=""),
        'reporter_pgp': '',
        'comm_attempt': 'False',
        'why_no_attempt': '',
        'please_explain': '',

        'ai_ml_system': True,
        'cisa_please': False,

        'vrf_id': report_id,
        'vrf_date_submitted': submitted,
        'remote_addr': '127.0.0.1',
        'remote_host': 'unknown',
        'http_user_agent': 'Unknown',
        'http_referer': 'https://bigvince-devtest-kb.testdit.org/vuls/vulcoordrequest/',
        'submission_type': submission_type,
        'title': title,
        'user_file': None,
    }

    return cert_json

if __name__ == "__main__":
    ai_flaw_example = "/Users/elainezhu/Downloads/ai_flaw_report_ef6fa01c-fccd-4430-b81f-d8953d3f70f0.json"
    cert_report = convert_to_cert_json(ai_flaw_example)
    print(json.dumps(cert_report, indent=2))
