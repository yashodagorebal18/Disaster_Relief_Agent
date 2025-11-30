import csv
import json
import math
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_SHELTERS = 'project/data/shelters.csv'
DATA_ORGS = 'project/data/organizations.json'

def load_shelters() -> List[Dict[str, Any]]:
    rows = []
    with open(DATA_SHELTERS, newline='', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            # normalize types
            row['lat'] = float(row['lat']) if row.get('lat') else None
            row['lon'] = float(row['lon']) if row.get('lon') else None
            rows.append(row)
    return rows

def load_orgs() -> List[str]:
    with open(DATA_ORGS, 'r', encoding='utf-8') as f:
        return json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    # returns distance in km
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def geocode_location(location: Dict[str, Any]) -> Dict[str, Any]:
    # For prototype, if lat/lon present return them; otherwise map city to known coords
    if location.get('lat') and location.get('lon'):
        return {'lat': location['lat'], 'lon': location['lon'], 'city': location.get('city')}
    if location.get('city') and location['city'].lower() == 'springfield':
        return {'lat': 40.7128, 'lon': -74.0060, 'city': 'Springfield'}
    return {'lat': None, 'lon': None, 'city': None}

def search_resources(query_terms: List[str], location: Dict[str, Any], max_results: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    rows = load_shelters()
    lat = location.get('lat')
    lon = location.get('lon')
    results = []
    for r in rows:
        score = 0
        kind = r.get('type','').lower()
        for term in query_terms:
            if term in kind:
                score += 2
        # distance
        if lat and lon and r.get('lat') and r.get('lon'):
            dist = haversine(lat, lon, r['lat'], r['lon'])
        else:
            dist = None
        # verification
        verified_by = r.get('verified_by')
        verified_score = 1 if verified_by else 0
        total_score = score + verified_score
        results.append({
            'record': r,
            'score': total_score,
            'distance_km': dist,
            'verified_by': verified_by,
            'last_updated': r.get('last_updated')
        })
    # ranking: prefer verified and closer
    def sort_key(x):
        v = 0 if not x['verified_by'] else 1
        d = x['distance_km'] if x['distance_km'] is not None else 9999
        return (-v, x['score'] * -1, d)
    results.sort(key=sort_key)
    return results[:max_results]

def summarize_resource(rec: Dict[str, Any]) -> str:
    r = rec.get('record', {})
    name = r.get('name', 'Resource')
    addr = r.get('address', 'Address not provided')
    note = r.get('notes', '')
    verified = rec.get('verified_by')
    last = rec.get('last_updated')
    s = f"{name} — {addr}."
    if note:
        s += f" Note: {note}."
    s += f" Verified by: {verified}. Last updated: {last}."
    if rec.get('distance_km') is not None:
        s += f" (~{rec['distance_km']:.1f} km)"
    return s

def verify_source(source: str) -> bool:
    orgs = load_orgs()
    return source in orgs

def check_recency(last_updated_iso: str, threshold_days: int = 90) -> bool:
    try:
        d = datetime.fromisoformat(last_updated_iso)
        delta = datetime.now() - d
        return delta.days <= threshold_days
    except Exception:
        return False
