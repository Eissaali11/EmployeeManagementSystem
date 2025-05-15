from app import db, app
from models import VehicleHandover

with app.app_context():
    # Print the columns of the VehicleHandover table
    print("VehicleHandover table columns:")
    for column in VehicleHandover.__table__.columns:
        print(f"- {column.name} ({column.type})")