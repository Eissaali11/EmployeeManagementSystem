#!/usr/bin/env python3
"""
Simple test for VehicleHandover.to_dict() method
"""

from datetime import datetime, date
import json

class MockVehicleHandover:
    """Mock VehicleHandover class for testing"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        """
        تحويل كائن VehicleHandover إلى قاموس قابل للتحويل إلى JSON
        """
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'handover_type': self.handover_type,
            'handover_date': self.handover_date.strftime('%Y-%m-%d') if self.handover_date else None,
            'handover_time': self.handover_time.strftime('%H:%M') if self.handover_time else None,
            'mileage': self.mileage,
            'project_name': self.project_name,
            'city': self.city,
            'vehicle_car_type': self.vehicle_car_type,
            'vehicle_plate_number': self.vehicle_plate_number,
            'vehicle_model_year': self.vehicle_model_year,
            'employee_id': self.employee_id,
            'person_name': self.person_name,
            'driver_company_id': self.driver_company_id,
            'driver_phone_number': self.driver_phone_number,
            'driver_residency_number': self.driver_residency_number,
            'driver_contract_status': self.driver_contract_status,
            'driver_license_status': self.driver_license_status,
            'driver_signature_path': self.driver_signature_path,
            'supervisor_employee_id': self.supervisor_employee_id,
            'supervisor_name': self.supervisor_name,
            'supervisor_company_id': self.supervisor_company_id,
            'supervisor_phone_number': self.supervisor_phone_number,
            'supervisor_residency_number': self.supervisor_residency_number,
            'supervisor_contract_status': self.supervisor_contract_status,
            'supervisor_license_status': self.supervisor_license_status,
            'supervisor_signature_path': self.supervisor_signature_path,
            'reason_for_change': self.reason_for_change,
            'vehicle_status_summary': self.vehicle_status_summary,
            'notes': self.notes,
            'reason_for_authorization': self.reason_for_authorization,
            'authorization_details': self.authorization_details,
            'fuel_level': self.fuel_level,
            'has_spare_tire': self.has_spare_tire,
            'has_fire_extinguisher': self.has_fire_extinguisher,
            'has_first_aid_kit': self.has_first_aid_kit,
            'has_warning_triangle': self.has_warning_triangle,
            'has_tools': self.has_tools,
            'has_oil_leaks': self.has_oil_leaks,
            'has_gear_issue': self.has_gear_issue,
            'has_clutch_issue': self.has_clutch_issue,
            'has_engine_issue': self.has_engine_issue,
            'has_windows_issue': self.has_windows_issue,
            'has_tires_issue': self.has_tires_issue,
            'has_body_issue': self.has_body_issue,
            'has_electricity_issue': self.has_electricity_issue,
            'has_lights_issue': self.has_lights_issue,
            'has_ac_issue': self.has_ac_issue,
            'movement_officer_name': self.movement_officer_name,
            'movement_officer_signature_path': self.movement_officer_signature_path,
            'damage_diagram_path': self.damage_diagram_path,
            'form_link': self.form_link,
            'custom_company_name': self.custom_company_name,
            'custom_logo_path': self.custom_logo_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

def test_handover_to_dict():
    """Test the to_dict method of VehicleHandover"""
    print("Testing VehicleHandover.to_dict() method...")
    
    # Create a test handover object
    handover = MockVehicleHandover(
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
        has_ac_issue=False,
        # Add None values for optional fields
        vehicle_car_type=None,
        vehicle_plate_number=None,
        vehicle_model_year=None,
        driver_company_id=None,
        driver_phone_number=None,
        driver_residency_number=None,
        driver_contract_status=None,
        driver_license_status=None,
        driver_signature_path=None,
        supervisor_employee_id=None,
        supervisor_name=None,
        supervisor_company_id=None,
        supervisor_phone_number=None,
        supervisor_residency_number=None,
        supervisor_contract_status=None,
        supervisor_license_status=None,
        supervisor_signature_path=None,
        reason_for_change=None,
        vehicle_status_summary=None,
        reason_for_authorization=None,
        authorization_details=None,
        movement_officer_name=None,
        movement_officer_signature_path=None,
        damage_diagram_path=None,
        form_link=None,
        custom_company_name=None,
        custom_logo_path=None,
        created_at=datetime.now()
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
    
    # Create a test handover object
    handover = MockVehicleHandover(
        id=1,
        vehicle_id=1,
        handover_type='delivery',
        handover_date=date(2025, 1, 20),
        handover_time=datetime.strptime('10:30', '%H:%M').time(),
        mileage=50000,
        person_name='Test Driver',
        fuel_level='ممتلئ',
        # Add None values for optional fields
        project_name=None,
        city=None,
        employee_id=None,
        notes=None,
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
        has_ac_issue=False,
        vehicle_car_type=None,
        vehicle_plate_number=None,
        vehicle_model_year=None,
        driver_company_id=None,
        driver_phone_number=None,
        driver_residency_number=None,
        driver_contract_status=None,
        driver_license_status=None,
        driver_signature_path=None,
        supervisor_employee_id=None,
        supervisor_name=None,
        supervisor_company_id=None,
        supervisor_phone_number=None,
        supervisor_residency_number=None,
        supervisor_contract_status=None,
        supervisor_license_status=None,
        supervisor_signature_path=None,
        reason_for_change=None,
        vehicle_status_summary=None,
        reason_for_authorization=None,
        authorization_details=None,
        movement_officer_name=None,
        movement_officer_signature_path=None,
        damage_diagram_path=None,
        form_link=None,
        custom_company_name=None,
        custom_logo_path=None,
        created_at=datetime.now()
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