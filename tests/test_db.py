import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.connect import engine

def test_connection():
    try:
        with engine.connect() as conn:
            print("Successfully connected to PostgreSQL!")
            assert True  # If it reaches here, the test passes
    except Exception as e:
        print(f"Connection failed: {e}")
        assert False  # If it fails, the test should fail

if __name__ == "__main__":
    test_connection()
