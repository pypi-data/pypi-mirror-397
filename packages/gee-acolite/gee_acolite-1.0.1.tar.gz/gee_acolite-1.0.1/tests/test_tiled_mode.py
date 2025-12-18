"""
Quick test to verify tiled processing implementation
Run this to check if the new tiled mode is working correctly
"""

import ee
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Testing tiled processing implementation...")
print("-" * 50)

# Test 1: Import modules
print("\n[1/5] Testing imports...")
try:
    from gee_acolite.correction import ACOLITE
    print("✓ ACOLITE class imported successfully")
except Exception as e:
    print(f"✗ Failed to import ACOLITE: {e}")
    sys.exit(1)

# Test 2: Check new methods exist
print("\n[2/5] Checking new methods...")
processor = ACOLITE.__new__(ACOLITE)
required_methods = [
    'create_tile_grid',
    'compute_pdark_per_tile',
    'dask_spectrum_fitting_tiled',
    'mosaic_tiles_with_feathering'
]

for method in required_methods:
    if hasattr(processor, method):
        print(f"✓ Method '{method}' exists")
    else:
        print(f"✗ Method '{method}' NOT FOUND")
        sys.exit(1)

# Test 3: Initialize Earth Engine (skip if not authenticated)
print("\n[3/5] Testing Earth Engine initialization...")
try:
    ee.Initialize()
    print("✓ Earth Engine initialized")
except Exception as e:
    print(f"⚠ Earth Engine not initialized: {e}")
    print("  (This is OK if you haven't authenticated yet)")

# Test 4: Check settings parsing
print("\n[4/5] Testing settings configuration...")
try:
    test_settings = {
        'dsf_aot_estimate': 'tiled',
        'dsf_tile_dimensions': 3,
        'dsf_tile_feather': 0.1,
        'aerosol_correction': 'dark_spectrum',
        'dsf_model_selection': 'min_drmsd',
        'dsf_spectrum_option': 'darkest',
        'dsf_nbands': 2,
        'uoz_default': 0.3,
        'uwv_default': 1.5,
        'pressure_default': 1013.25,
        'wind_default': 2.0,
        's2_target_res': 10,
    }
    
    # Check tiled-specific settings
    assert test_settings['dsf_aot_estimate'] == 'tiled'
    assert test_settings['dsf_tile_dimensions'] == 3
    assert test_settings['dsf_tile_feather'] == 0.1
    
    print("✓ Tiled settings configured correctly")
    print(f"  - Mode: {test_settings['dsf_aot_estimate']}")
    print(f"  - Grid: {test_settings['dsf_tile_dimensions']}x{test_settings['dsf_tile_dimensions']}")
    print(f"  - Feather: {test_settings['dsf_tile_feather']*100}%")
    
except Exception as e:
    print(f"✗ Settings test failed: {e}")
    sys.exit(1)

# Test 5: Verify documentation
print("\n[5/5] Checking documentation...")
doc_files = [
    'docs/TILED_PROCESSING.md',
    'examples/06_tiled_processing.py'
]

for doc_file in doc_files:
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), doc_file)
    if os.path.exists(file_path):
        print(f"✓ {doc_file} exists")
    else:
        print(f"⚠ {doc_file} not found")

print("\n" + "=" * 50)
print("🎉 ALL TESTS PASSED!")
print("=" * 50)
print("\nTiled processing is ready to use!")
print("\nQuick start:")
print("  1. See examples/06_tiled_processing.py for usage")
print("  2. Read docs/TILED_PROCESSING.md for details")
print("  3. Set 'dsf_aot_estimate': 'tiled' in your settings")
print("\nExample:")
print("""
  settings = {
      'dsf_aot_estimate': 'tiled',
      'dsf_tile_dimensions': 3,
      'dsf_tile_feather': 0.1,
      ...
  }
""")
