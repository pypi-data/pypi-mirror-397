import os
import warnings

from dotenv import load_dotenv

from transaud.utils import get_lib_dir

try:
    cwd = get_lib_dir()
    env_path = f"{cwd}/.env"
    load_dotenv(dotenv_path=env_path)
except:
    warnings.warn(".env file not found. Ensure `HF_TOKEN` is registered in environment variables.")


HF_TOKEN = os.environ.get("HF_TOKEN")

