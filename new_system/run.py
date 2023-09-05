from app import create_app, db
from app.models import GlobalConfig  # Import your model here

def create_tables(app):
    with app.app_context():
        db.create_all()  # Create all tables

        # Check if a row already exists
        existing_row = GlobalConfig.query.get(1)  # Trying to get the row with ID=1

        # If it doesn't exist, create it
        if existing_row is None:
            default_config = GlobalConfig(
                # Add default values for your columns here
                # For example:
                # session_name='default_session',
                # project_dir='/default/path'
            )
            db.session.add(default_config)
            db.session.commit()

if __name__ == '__main__':
    app = create_app()

    # Create tables and add default data
    create_tables(app)

    app.run(debug=True, host="0.0.0.0", port=7777)
