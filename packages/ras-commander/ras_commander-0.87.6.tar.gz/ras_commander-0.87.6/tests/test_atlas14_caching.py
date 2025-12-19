"""
Test NOAA Atlas 14 caching functionality.

Tests the LLM Forward pattern of saving verifiable raw data to project folders.
"""

from pathlib import Path
import shutil
import tempfile
from ras_commander.precip import StormGenerator

def test_atlas14_caching():
    """Test Atlas 14 download, cache, and reuse."""

    # Create temporary test folder
    with tempfile.TemporaryDirectory() as temp_dir:
        project_folder = Path(temp_dir) / "test_project"
        project_folder.mkdir()

        # Test coordinates (Washington, DC)
        lat, lon = 38.9, -77.0

        print("\n" + "="*70)
        print("ATLAS 14 CACHING TEST")
        print("="*70)

        # Test 1: First download (should hit API)
        print("\n[Test 1] First download - should hit NOAA API...")
        gen1 = StormGenerator.download_from_coordinates(
            lat, lon,
            project_folder=project_folder
        )

        # Verify cache file created
        cache_dir = project_folder / "NOAA_Atlas_14"
        cache_file = cache_dir / f"lat{lat}_lon{lon}_depth_english_pds.json"

        assert cache_dir.exists(), "Cache directory not created"
        assert cache_file.exists(), "Cache file not created"
        print(f"[OK] Cache created: {cache_file}")

        # Verify we can generate hyetograph
        hyeto1 = gen1.generate_hyetograph(ari=100, duration_hours=24)
        print(f"[OK] Generated hyetograph: {len(hyeto1)} time steps")
        print(f"  Total depth: {hyeto1['cumulative_depth'].iloc[-1]:.3f} inches")

        # Test 2: Second download (should use cache)
        print("\n[Test 2] Second download - should use cache...")
        gen2 = StormGenerator.download_from_coordinates(
            lat, lon,
            project_folder=project_folder,
            use_cache=True
        )

        # Verify hyetograph matches
        hyeto2 = gen2.generate_hyetograph(ari=100, duration_hours=24)
        assert len(hyeto1) == len(hyeto2), "Hyetograph length mismatch"
        assert abs(hyeto1['cumulative_depth'].iloc[-1] - hyeto2['cumulative_depth'].iloc[-1]) < 0.001, \
            "Hyetograph depth mismatch"
        print(f"[OK] Cached data matches original")

        # Test 3: Force fresh download (should hit API again)
        print("\n[Test 3] Force fresh download - should hit API...")
        gen3 = StormGenerator.download_from_coordinates(
            lat, lon,
            project_folder=project_folder,
            use_cache=False  # Force fresh download
        )

        hyeto3 = gen3.generate_hyetograph(ari=100, duration_hours=24)
        assert abs(hyeto1['cumulative_depth'].iloc[-1] - hyeto3['cumulative_depth'].iloc[-1]) < 0.001, \
            "Fresh download depth mismatch"
        print(f"[OK] Fresh download matches original")

        # Test 4: Verify cache file is human-readable JSON
        print("\n[Test 4] Verify cache file format...")
        import json
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)

        assert 'quantiles' in cached_data, "Missing quantiles in cache"
        assert 'region' in cached_data, "Missing region in cache"
        assert 'lat' in cached_data, "Missing lat in cache"
        assert 'lon' in cached_data, "Missing lon in cache"
        print(f"[OK] Cache is valid JSON")
        print(f"  Region: {cached_data.get('region', 'Unknown')}")
        print(f"  Lat/Lon: ({cached_data.get('lat')}, {cached_data.get('lon')})")
        print(f"  Quantiles: {len(cached_data.get('quantiles', []))} durations")

        # Test 5: Load using static method directly
        print("\n[Test 5] Direct load from cache...")
        loaded_data = StormGenerator.load_atlas14_raw_data(
            project_folder, lat, lon
        )
        assert loaded_data is not None, "Failed to load from cache"
        assert loaded_data['region'] == cached_data['region'], "Loaded data mismatch"
        print(f"[OK] Direct load successful")

        # Test 6: Cache miss for different coordinates
        print("\n[Test 6] Cache miss for different coordinates...")
        different_data = StormGenerator.load_atlas14_raw_data(
            project_folder, 40.7, -74.0  # New York City
        )
        assert different_data is None, "Should be cache miss for different coords"
        print(f"[OK] Cache miss detected correctly")

        print("\n" + "="*70)
        print("ALL TESTS PASSED")
        print("="*70)
        print(f"\nCache location: {cache_file}")
        print(f"File size: {cache_file.stat().st_size / 1024:.1f} KB")
        print("\nLLM Forward Verification:")
        print("  - Raw NOAA data saved to project folder [OK]")
        print("  - Human-readable JSON format [OK]")
        print("  - Automatic cache reuse [OK]")
        print("  - Force fresh download option [OK]")

if __name__ == "__main__":
    test_atlas14_caching()
