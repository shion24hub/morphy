import configparser
import os
import time
from functools import wraps
from pathlib import Path

from .. import config


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.2f} sec")
        return result

    return wrapper


def find_storage_path() -> Path:
    parser = configparser.ConfigParser()
    parser.read(os.path.join(config.PROJECT_DIR, "morphy.ini"))

    try:
        storage_dir = parser["PATHS"]["STORAGE_DIR"]
    except KeyError:
        err = "Storage directory not found in `morphy.ini`."
        raise ValueError(err)

    return Path(storage_dir)
