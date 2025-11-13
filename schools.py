#!/usr/bin/env python3
"""
fetch_schools_contacts_pretty.py

Fetches: https://digital.edu.az/backend-api/schools
Bypasses self-signed SSL (verify=False).
Extracts requested fields, converts contacts JSON into readable columns,
and writes CSV + XLSX + raw JSON.

Outputs:
 - raw_response.json
 - schools.csv
 - schools.xlsx

Requires:
 pip install requests pandas openpyxl
"""

from typing import Any, Dict, List, Sequence, Tuple
import requests
import json
import time
import sys
import urllib3
import pandas as pd

API_URL = "https://digital.edu.az/backend-api/schools"
OUT_CSV = "schools.csv"
OUT_XLSX = "schools.xlsx"
RAW_JSON = "raw_response.json"

TIMEOUT = 10
MAX_RETRIES = 4
RETRY_BACKOFF = 2.0

REQUESTED_COLUMNS: Sequence[str] = [
    "address",
    "contacts",         # semicolon-joined values (human readable)
    "contacts_phones",  # phone values only (typeId==1) joined by |
    "contacts_emails",  # email values only (typeId==3) joined by ;
    "contacts_json",    # original JSON string (audit)
    "hasJurnal",
    "hasMeeting",
    "id",
    "imageToken",
    "lat",
    "lng",
    "name",
    "regionId",
    "regionName",
    "schoolKind",
    "schoolKindId",
    "schoolType",
    "schoolTypeId",
    "siteUrl",
    "subjection",
    "subjectionId",
    "utisCode",
]

CANDIDATE_PATHS: Dict[str, List[str]] = {
    "address": ["address", "addressText", "location.address", "location", "adress"],
    "contacts": ["contacts", "contact", "contactsList", "phones", "emails"],
    "hasJurnal": ["hasJurnal", "hasJournal", "has_jurnal", "has_journal"],
    "hasMeeting": ["hasMeeting", "has_meeting"],
    "id": ["id", "schoolId", "school_id"],
    "imageToken": ["imageToken", "image_token", "image.token", "imageTokenName", "image"],
    "lat": ["lat", "latitude", "location.lat", "location.latitude"],
    "lng": ["lng", "lon", "long", "longitude", "location.lng", "location.longitude"],
    "name": ["name", "schoolName", "title"],
    "regionId": ["regionId", "region_id", "region.id", "regionId"],
    "regionName": ["regionName", "region_name", "region.name", "region"],
    "schoolKind": ["schoolKind", "school_kind", "kind", "schoolKindName"],
    "schoolKindId": ["schoolKindId", "school_kind_id", "schoolKind.id"],
    "schoolType": ["schoolType", "school_type", "type", "schoolTypeName"],
    "schoolTypeId": ["schoolTypeId", "school_type_id", "schoolType.id"],
    "siteUrl": ["siteUrl", "site_url", "website", "site"],
    "subjection": ["subjection", "subjectionName", "subjection.name", "authority"],
    "subjectionId": ["subjectionId", "subjection_id", "subjection.id", "authorityId"],
    "utisCode": ["utisCode", "utis_code", "utis", "utisId"],
}

def fetch_json(url: str) -> Any:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT, verify=False)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_exc = e
            wait = RETRY_BACKOFF ** attempt
            print(f"[warn] fetch attempt {attempt}/{MAX_RETRIES} failed: {e}. retrying in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_exc}")

def extract_records(root_json: Any) -> List[Dict[str, Any]]:
    if root_json is None:
        return []
    if isinstance(root_json, list):
        return root_json
    if isinstance(root_json, dict):
        for key in ("data", "items", "results", "schools", "rows"):
            if key in root_json:
                if isinstance(root_json[key], list):
                    return root_json[key]
                elif isinstance(root_json[key], dict):
                    return [root_json[key]]
        if all(isinstance(v, dict) for v in root_json.values()) and len(root_json) > 0:
            return list(root_json.values())
        return [root_json]
    return []

def get_by_path(obj: Dict[str, Any], path: str) -> Any:
    node = obj
    for part in path.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node

def normalize_contacts_field(raw_val: Any) -> Tuple[str, str, str, str]:
    """
    Input: raw_val may be:
      - list of dicts each containing at least 'value' and maybe 'typeId'
      - string (maybe already JSON or semicolon list)
      - dict (single contact)
      - None

    Returns tuple:
      (contacts_all, contacts_phones, contacts_emails, contacts_json)
    contacts_all: ';' joined list of all 'value' fields in original order (or string cleaned)
    contacts_phones: '|' joined values where typeId==1 (heuristic)
    contacts_emails: ';' joined values where typeId==3 (heuristic)
    contacts_json: compact JSON string of the original list/dict (or '[]'/'')
    """
    if raw_val is None:
        return ("", "", "", "")

    # If it's already a JSON string (looks like array/object), try parse
    if isinstance(raw_val, str):
        s = raw_val.strip()
        # detect JSON-like
        if s.startswith("[") or s.startswith("{"):
            try:
                parsed = json.loads(s)
                raw_val = parsed
            except Exception:
                # not JSON, treat as semicolon-separated list of values
                parts = [p.strip() for p in s.split(";") if p.strip()]
                contacts_all = ";".join(parts)
                return (contacts_all, "", contacts_all, s)
        else:
            # simple plain string (e.g., "a@x.com;tel"): split by semicolon
            parts = [p.strip() for p in s.split(";") if p.strip()]
            contacts_all = ";".join(parts)
            return (contacts_all, "", contacts_all, s)

    # Now raw_val is likely list or dict
    items = []
    if isinstance(raw_val, dict):
        items = [raw_val]
    elif isinstance(raw_val, list):
        items = raw_val
    else:
        # fallback: convert to string
        s = str(raw_val)
        parts = [p.strip() for p in s.split(";") if p.strip()]
        contacts_all = ";".join(parts)
        return (contacts_all, "", contacts_all, s)

    values_all: List[str] = []
    phones: List[str] = []
    emails: List[str] = []

    for it in items:
        if not isinstance(it, dict):
            # if it's a primitive, use as-is
            v = str(it).strip()
            if v:
                values_all.append(v)
            continue
        v = it.get("value") if "value" in it else None
        t = it.get("typeId") if "typeId" in it else it.get("type") if "type" in it else None
        # fallback to other keys if necessary
        if v is None:
            # try other common keys
            for key in ("val", "phone", "email"):
                if key in it:
                    v = it.get(key)
                    break
        if v is None:
            # skip if no value
            continue
        v = str(v).strip()
        values_all.append(v)
        # type heuristics: numeric typeId 1 -> phone, 3 -> email
        try:
            t_int = int(t) if t is not None else None
        except Exception:
            t_int = None
        # simple heuristics if typeId absent: check if value contains '@'
        if t_int == 1:
            phones.append(v)
        elif t_int == 3:
            emails.append(v)
        else:
            # unknown type: guess
            if "@" in v and "." in v:
                emails.append(v)
            else:
                # treat as phone-like if digits exist
                digits = "".join(ch for ch in v if ch.isdigit())
                if len(digits) >= 5:
                    phones.append(v)
                else:
                    # ambiguous — keep in all but not in phones/emails
                    pass

    contacts_all = ";".join(values_all)
    contacts_phones = "|".join(phones)
    contacts_emails = ";".join(emails)
    try:
        contacts_json = json.dumps(items, ensure_ascii=False)
    except Exception:
        contacts_json = str(items)
    return (contacts_all, contacts_phones, contacts_emails, contacts_json)

def resolve_field(record: Dict[str, Any], field_name: str) -> Any:
    candidates = CANDIDATE_PATHS.get(field_name, [field_name])
    for p in candidates:
        val = get_by_path(record, p)
        if val is None:
            continue
        if field_name.startswith("contacts"):
            # we handle contacts separately in prepare_rows
            return val
        if field_name == "imageToken" and isinstance(val, dict):
            for k in ("token", "fileName", "file", "name", "imageToken"):
                if k in val and val[k]:
                    return val[k]
            return json.dumps(val, ensure_ascii=False)
        if field_name in ("lat", "lng"):
            try:
                return float(str(val).replace(",", "."))
            except Exception:
                return val
        if field_name in ("hasJurnal", "hasMeeting"):
            if isinstance(val, bool):
                return val
            if str(val).lower() in ("1", "true", "yes"):
                return True
            if str(val).lower() in ("0", "false", "no", ""):
                return False
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        return val
    return ""

def flatten(obj: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    items: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(flatten(v, new_key, sep))
            elif isinstance(v, list):
                try:
                    items[new_key] = json.dumps(v, ensure_ascii=False)
                except Exception:
                    items[new_key] = str(v)
            else:
                items[new_key] = v
    else:
        items[parent_key or "value"] = obj
    return items

def prepare_rows(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for rec in records:
        row: Dict[str, Any] = {}
        # Resolve requested non-contacts columns first
        for col in REQUESTED_COLUMNS:
            if col in ("contacts", "contacts_phones", "contacts_emails", "contacts_json"):
                # we'll compute these below
                row[col] = ""
                continue
            row[col] = resolve_field(rec, col)
        # Extract raw contacts raw value from the record using candidate paths
        raw_contacts_val = None
        # try canonical 'contacts' resolution paths
        for p in CANDIDATE_PATHS.get("contacts", ["contacts"]):
            candidate = get_by_path(rec, p)
            if candidate is not None:
                raw_contacts_val = candidate
                break
        # fallback: top-level 'contacts' key
        if raw_contacts_val is None and "contacts" in rec:
            raw_contacts_val = rec["contacts"]

        # normalize contacts
        contacts_all, contacts_phones, contacts_emails, contacts_json = normalize_contacts_field(raw_contacts_val)
        row["contacts"] = contacts_all
        row["contacts_phones"] = contacts_phones
        row["contacts_emails"] = contacts_emails
        row["contacts_json"] = contacts_json

        # Flatten and add extra fields without overwriting
        flat = flatten(rec)
        for k, v in flat.items():
            if k in row:
                continue
            row[k] = v
        rows.append(row)
    return rows

def save_outputs(rows: List[Dict[str, Any]]):
    if not rows:
        raise RuntimeError("No rows to save.")
    extra_keys = sorted({k for r in rows for k in r.keys()} - set(REQUESTED_COLUMNS))
    columns = list(REQUESTED_COLUMNS) + extra_keys
    df = pd.DataFrame(rows, columns=columns)
    # Save CSV and XLSX
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    df.to_excel(OUT_XLSX, index=False, engine="openpyxl")
    print(f"[ok] Saved {len(df)} rows -> {OUT_CSV} and {OUT_XLSX}")

def main():
    print(f"[info] Fetching {API_URL}")
    root = fetch_json(API_URL)
    with open(RAW_JSON, "w", encoding="utf-8") as fh:
        json.dump(root, fh, ensure_ascii=False, indent=2)
    print(f"[info] Raw JSON saved to {RAW_JSON}")
    records = extract_records(root)
    if not records:
        print("[warn] No records found.")
        sys.exit(3)
    print(f"[info] Found {len(records)} record(s). Preparing rows...")
    rows = prepare_rows(records)
    # Print sample of contacts transformation for visual verification
    print("[info] Sample contacts (first record):")
    first = rows[0]
    sample_contacts = {
        "contacts": first.get("contacts"),
        "contacts_phones": first.get("contacts_phones"),
        "contacts_emails": first.get("contacts_emails"),
        "contacts_json": first.get("contacts_json")[:200] + ("..." if len(first.get("contacts_json",""))>200 else "")
    }
    print(json.dumps(sample_contacts, ensure_ascii=False, indent=2))
    save_outputs(rows)

if __name__ == "__main__":
    main()
