#!/usr/bin/env python3
"""
Test script to verify edit handover functionality
"""

import requests
import json

def test_edit_handover():
    """Test the edit handover functionality"""
    
    # Base URL for the application
    base_url = "http://localhost:5000"
    
    # Test data for creating a handover
    test_handover_data = {
        'vehicle_id': '1',  # Assuming vehicle with ID 1 exists
        'handover_type': 'delivery',
        'handover_date': '2025-01-20',
        'handover_time': '10:30',
        'person_name': 'Test Driver',
        'employee_id': '1',  # Assuming employee with ID 1 exists
        'mileage': '50000',
        'fuel_level': 'ممتلئ',
        'project_name': 'Test Project',
        'city': 'Riyadh',
        'reason_for_change': 'Test handover',
        'notes': 'Test notes',
        'has_spare_tire': 'on',
        'has_fire_extinguisher': 'on',
        'has_first_aid_kit': 'on',
        'has_warning_triangle': 'on',
        'has_tools': 'on'
    }
    
    print("Testing edit handover functionality...")
    
    # Test 1: Create a new handover
    print("1. Creating a new handover...")
    try:
        response = requests.post(f"{base_url}/mobile/vehicles/checklist", data=test_handover_data)
        if response.status_code == 200:
            print("✓ Handover creation endpoint accessible")
        else:
            print(f"✗ Handover creation failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing handover creation: {e}")
    
    # Test 2: Test edit handover route
    print("2. Testing edit handover route...")
    try:
        # Test with a hypothetical handover ID
        response = requests.get(f"{base_url}/mobile/vehicles/handover/1/edit")
        if response.status_code == 302:  # Redirect expected
            print("✓ Edit handover route redirects correctly")
        else:
            print(f"✗ Edit handover route returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing edit handover route: {e}")
    
    # Test 3: Test the checklist route with handover_id parameter
    print("3. Testing checklist route with handover_id...")
    try:
        response = requests.get(f"{base_url}/mobile/vehicles/checklist/1")
        if response.status_code == 200:
            print("✓ Checklist route with handover_id accessible")
        else:
            print(f"✗ Checklist route with handover_id returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing checklist route: {e}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_edit_handover() 