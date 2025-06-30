import os
from dotenv import load_dotenv


def test_environment_variables_loaded():
    load_dotenv()
    assert os.getenv('DATABASE_URL') is not None
    assert os.getenv('NOMINATIM_BASE_URL') is not None
    assert os.getenv('LOG_LEVEL') is not None
    print("✅ Environment configuration validated")