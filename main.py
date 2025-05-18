from app import app
from routes.workshop_reports import workshop_reports_bp

# تسجيل blueprint
app.register_blueprint(workshop_reports_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
