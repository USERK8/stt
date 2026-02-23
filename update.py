# update.py

import os
import requests
from PyQt6.QtWidgets import QMessageBox

# GitHub repo raw URLs
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/USERK8/stt/main/"
VERSION_FILE = "version.txt"

# List of files to update (add all your app files here)
FILES_TO_UPDATE = [
    "main.py",
    "mc.py",
    "mt.py",
    "mts.py",
    "s.py",
    "get.py",
    "rules.py",
    "classes.json",
    "msc.json",
    "teach_dat.json",
    "version.txt",
    "update.py",
    "about this folder",
    "class.json",
]


def fetch_remote_version():
    url = GITHUB_RAW_BASE + VERSION_FILE
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        print("Error fetching remote version:", e)
        return None

def fetch_local_version():
    if not os.path.exists(VERSION_FILE):
        return "0.0.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def download_file(file_name):
    url = GITHUB_RAW_BASE + file_name
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(file_name, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"Failed to download {file_name}: {e}")
        return False

def check_for_update(parent=None):
    remote_version = fetch_remote_version()
    local_version = fetch_local_version()
    if not remote_version:
        return False  # cannot check

    if remote_version > local_version:
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Update Available")
        msg.setText(f"A new version ({remote_version}) is available.\nYour version: {local_version}")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        ret = msg.exec()

        if ret == QMessageBox.StandardButton.Yes:
            success_files = []
            failed_files = []
            for f in FILES_TO_UPDATE:
                if download_file(f):
                    success_files.append(f)
                else:
                    failed_files.append(f)

            if failed_files:
                msg2 = QMessageBox(parent)
                msg2.setIcon(QMessageBox.Icon.Critical)
                msg2.setWindowTitle("Update Failed")
                msg2.setText(f"Some files could not be updated:\n{', '.join(failed_files)}")
                msg2.exec()
            else:
                msg3 = QMessageBox(parent)
                msg3.setIcon(QMessageBox.Icon.Information)
                msg3.setWindowTitle("Update Complete")
                msg3.setText("All files updated successfully!\nPlease restart the app.")
                msg3.exec()
                return True
    return False
