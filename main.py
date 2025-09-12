import os
import json
from pathlib import Path
from datetime import datetime
import shutil
import argparse
import logging

# CLI arguments
parser = argparse.ArgumentParser(description="File organzer script")
parser.add_argument("--path", type=str, required=True, help="Path to folder to organize")
parser.add_argument("--dry-run", action="store_true", help="Previewmoves without changing files")
parser.add_argument("--recursive", action="store_true", help="Organize files recursively in subfolders")
args = parser.parse_args()

folder_path = Path(args.path)
if not folder_path.exists() or not folder_path.is_dir():
    print("Provided path does not exist or is not a directory")
    exit()
#setup logging
log_file = folder_path / "file_organizer.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("starting file organization for : %s", folder_path)

# load config
config_file = Path("config.json")
if not config_file.exists():
    print("config.json file not found")
    exit()

with open("config.json", "r") as f:
    config = json.load(f)


#helper function to get category
def get_category(file_ext):
    for category, extensions in config.items():
        if file_ext.lower() in extensions:
            return category
        return "others"

def organize_folder(path):
    for item in path.iterdir():
        if item.is_file():
            ext = item.suffix
            category = get_category(ext)

            # File's modified date
            mod_time = datetime.fromtimestamp(item.stat().st_mtime)
            year = mod_time.year
            month = mod_time.month

            # Destination folder
            dest_folder = folder_path / category / str(year) / f"{month:02d}"
            if not args.dry_run:
                dest_folder.mkdir(parents=True, exist_ok=True)

            # Destination file path
            dest_file = dest_folder / item.name

            # Handle duplicates
            counter = 1
            while dest_file.exists():
                dest_file = dest_folder / f"{item.stem}_{counter}{item.suffix}"
                counter += 1
            
            #actions
            if args.dry_run:
                print(f"[DRY-RUN] {item} --> {dest_file}")
                logging.info("[DRY-RUN] %s --> %s", item, dest_file)
            else:
                shutil.move(str(item), str(dest_file))
                print(f"Moved: {item} --> {dest_file}")
                logging.info("Moved: %s --> %s", item, dest_file)

        elif item.is_dir() and args.recursive:
            organize_folder(item)

# Start organizing
organize_folder(folder_path)

logging.info("file organization complete.")
print("organization complete.")
       

