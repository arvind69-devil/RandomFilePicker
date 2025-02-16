import os
import random
import json
from tkinter import messagebox
import subprocess

# Cache file path
CACHE_FILE = "cache.json"

def select_random_file(directory):
    # List all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    # Check if there are any files in the directory
    if not files:
        print("No files found in the directory.")
        return None
    
    # Select a random file
    random_file = random.choice(files)
    return os.path.join(directory, random_file)

def open_file(file_path):
    # Open the file with the default application
    if os.name == 'nt':  # Windows
        os.startfile(file_path)
    elif os.name == 'posix':  # macOS or Linux
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.run([opener, file_path])

def load_cache():
    # Load the cache from the JSON file
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    # Save the cache to the JSON file
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def add_to_cache(file_path, action=None):
    # Add a file to the cache
    cache = load_cache()
    cache[file_path] = {"action": action}
    save_cache(cache)

def get_cached_files():
    # Get all files from the cache
    cache = load_cache()
    return cache

def clear_cache():
    # Clear the cache
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)