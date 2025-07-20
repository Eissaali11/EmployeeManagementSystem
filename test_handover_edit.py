#!/usr/bin/env python3
"""
Test script to verify handover edit functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import VehicleHandover, Vehicle, Employee, db
from datetime import datetime, date

def test_handover_to_dict():
    """Test the to_dict method of VehicleHandover"""
    print("Testing VehicleHandover.to_dict() method...")
    
    # Create a test handover object
    handover = VehicleHandover(
        id=1,
        vehicle_id=1,
        handover_type='delivery',
        handover_date=date(2025, 1, 20),
        handover_time=datetime.strptime('10:30', '%H:%M').time(),
        mileage=50000,
        project_name='Test Project',
        city='Riyadh',
        person_name='Test Driver',
        employee_id=1,
        fuel_level='ممتلئ',
        notes='Test notes',
        has_spare_tire=True,
        has_fire_extinguisher=True,
        has_first_aid_kit=True,
        has_warning_triangle=True,
        has_tools=True,
        has_oil_leaks=False,
        has_gear_issue=False,
        has_clutch_issue=False,
        has_engine_issue=False,
        has_windows_issue=False,
        has_tires_issue=False,
        has_body_issue=False,
        has_electricity_issue=False,
        has_lights_issue=False,
        has_ac_issue=False
    )
    
    try:
        # Test the to_dict method
        handover_dict = handover.to_dict()
        
        # Verify the conversion worked
        assert isinstance(handover_dict, dict), "to_dict() should return a dictionary"
        assert 'id' in handover_dict, "Dictionary should contain 'id'"
        assert 'vehicle_id' in handover_dict, "Dictionary should contain 'vehicle_id'"
        assert 'handover_type' in handover_dict, "Dictionary should contain 'handover_type'"
        assert 'person_name' in handover_dict, "Dictionary should contain 'person_name'"
        assert 'mileage' in handover_dict, "Dictionary should contain 'mileage'"
        assert 'fuel_level' in handover_dict, "Dictionary should contain 'fuel_level'"
        
        # Verify date formatting
        assert handover_dict['handover_date'] == '2025-01-20', "Date should be formatted as YYYY-MM-DD"
        assert handover_dict['handover_time'] == '10:30', "Time should be formatted as HH:MM"
        
        # Verify boolean values
        assert handover_dict['has_spare_tire'] is True, "Boolean values should be preserved"
        assert handover_dict['has_oil_leaks'] is False, "Boolean values should be preserved"
        
        print("✓ VehicleHandover.to_dict() method works correctly!")
        print(f"  - Converted {len(handover_dict)} fields")
        print(f"  - Sample data: {handover_dict['person_name']} - {handover_dict['handover_type']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing to_dict(): {e}")
        return False

def test_json_serialization():
    """Test JSON serialization of the handover dictionary"""
    print("\nTesting JSON serialization...")
    
    import json
    
    # Create a test handover object
    handover = VehicleHandover(
        id=1,
        vehicle_id=1,
        handover_type='delivery',
        handover_date=date(2025, 1, 20),
        handover_time=datetime.strptime('10:30', '%H:%M').time(),
        mileage=50000,
        person_name='Test Driver',
        fuel_level='ممتلئ'
    )
    
    try:
        # Convert to dictionary
        handover_dict = handover.to_dict()
        
        # Test JSON serialization
        json_string = json.dumps(handover_dict, ensure_ascii=False)
        
        # Test JSON deserialization
        deserialized = json.loads(json_string)
        
        assert deserialized['id'] == 1, "JSON serialization should preserve data"
        assert deserialized['person_name'] == 'Test Driver', "JSON serialization should preserve data"
        assert deserialized['handover_type'] == 'delivery', "JSON serialization should preserve data"
        
        print("✓ JSON serialization works correctly!")
        print(f"  - JSON length: {len(json_string)} characters")
        print(f"  - Contains Arabic text: {'نعم' if 'ممتلئ' in json_string else 'لا'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing JSON serialization: {e}")
        return False

if __name__ == "__main__":
    print("Testing VehicleHandover edit functionality...\n")
    
    # Run tests
    test1_passed = test_handover_to_dict()
    test2_passed = test_json_serialization()
    
    print(f"\nTest Results:")
    print(f"  - to_dict() method: {'✓ PASS' if test1_passed else '✗ FAIL'}")
    print(f"  - JSON serialization: {'✓ PASS' if test2_passed else '✗ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The edit functionality should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.") 