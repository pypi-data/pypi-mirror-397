"""Diagnostic script to check NOAA API response."""

from ras_commander.precip import StormGenerator
import json

# Test coordinates
lat, lon = 38.9, -77.0

print(f"Testing NOAA Atlas 14 API for ({lat}, {lon})")
print("="*70)

# Make direct API call to see raw response
import urllib.request

params = {
    'lat': lat,
    'lon': lon,
    'type': 'pf',
    'data': 'depth',
    'units': 'english',
    'series': 'pds'
}
query_string = '&'.join(f"{k}={v}" for k, v in params.items())
url = f"{StormGenerator.NOAA_API_URL}?{query_string}"

print(f"\nURL: {url}\n")

try:
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'ras-commander/1.0')

    with urllib.request.urlopen(request, timeout=30) as response:
        content = response.read().decode('utf-8')

    print("Raw API Response (first 500 chars):")
    print("-"*70)
    print(content[:500])
    print("...")
    print("-"*70)

    # Debug: show statement splitting
    statements = content.replace('\n', ';').split(';')
    print(f"\nTotal statements: {len(statements)}")
    print("First 5 statements:")
    for i, stmt in enumerate(statements[:5]):
        print(f"  {i+1}. {stmt[:60] if len(stmt) > 60 else stmt}")

    # Parse response
    data_dict = StormGenerator._parse_noaa_response(content)

    print("\nParsed keys:")
    print(f"Total keys: {len(data_dict)}")
    for key in sorted(data_dict.keys()):
        val_type = type(data_dict[key]).__name__
        val_preview = str(data_dict[key])[:50] if len(str(data_dict[key])) > 50 else str(data_dict[key])
        print(f"  - {key}: {val_type} = {val_preview}")

    # Save to file for inspection
    with open("atlas14_response.json", 'w') as f:
        json.dump(data_dict, f, indent=2)

    print(f"\nFull response saved to: atlas14_response.json")

    if 'quantiles' in data_dict:
        print(f"\n[OK] quantiles found: {len(data_dict['quantiles'])} durations")
    else:
        print(f"\n[ERROR] quantiles NOT FOUND in response")
        print(f"\nAvailable keys: {list(data_dict.keys())}")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
