from app.database import engine, Base
from app import models

if __name__ == "__main__":
    print("Connecting to Postgres and creating tables...")
    
    Base.metadata.create_all(bind=engine)
    
    print("Tables created successfully!")