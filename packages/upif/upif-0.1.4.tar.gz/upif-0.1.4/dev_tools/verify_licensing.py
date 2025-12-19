import time
from upif.core.licensing import LicenseManager
from mock_gumroad import run_mock_server

# 1. Start Mock Server
print("Starting Mock Gumroad Server...")
server = run_mock_server(port=8000)
time.sleep(1)

# 2. Patch URL to point to localhost
LicenseManager.PRODUCT_PERMALINK = "test-product"
original_url = "https://api.gumroad.com/v2/licenses/verify"

# We must mock the request call inside LicenseManager instance or just valid URL
# Since we can't easily patch the class method URL variable locally without modifying code,
# we will rely on requests mocking or just override the instance method if possible.
# Actually, the implementation uses a hardcoded URL. Let's make it configurable for testing or patch 'requests.post'.

import requests
original_post = requests.post

def mock_post(url, data, timeout):
    if "api.gumroad.com" in url:
        # Redirect to our mock
        return original_post("http://localhost:8000/verify", data=data, timeout=timeout)
    return original_post(url, data, timeout)

requests.post = mock_post

# 3. Test Activation
lm = LicenseManager()
print("\n--- Test 1: Invalid Key ---")
success = lm.activate("INVALID-KEY")
print(f"Activation Result (Expected False): {success}")
assert not success
assert lm.get_tier() == "BASELINE"

print("\n--- Test 2: Valid Key ---")
success = lm.activate("TEST-PRO-KEY")
print(f"Activation Result (Expected True): {success}")
assert success
assert lm.get_tier() == "PRO"

# 4. Test Offline Persistence
print("\n--- Test 3: Offline Persistence ---")
lm2 = LicenseManager() # New instance
is_valid = lm2.validate_offline()
print(f"Offline Validation (Expected True): {is_valid}")
assert is_valid
assert lm2.get_tier() == "PRO"

print("\n--- SUCCESS: Licensing System Verified! ---")
