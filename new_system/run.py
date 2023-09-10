from app import create_app, db
from app.models import GlobalConfig 

def create_tables(app):
    with app.app_context():
        db.create_all() 

        existing_row = GlobalConfig.query.get(1)  


        #If the database do not exist, it will be created here
        if existing_row is None:
            default_config = GlobalConfig(

            )
            db.session.add(default_config)
            db.session.commit()

if __name__ == '__main__':
    app = create_app()

    create_tables(app)

    app.run(debug=True, host="0.0.0.0", port=7777)
