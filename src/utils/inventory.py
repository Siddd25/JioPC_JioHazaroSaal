
from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml
import json
from datetime import datetime
import time
import shutil
import subprocess
import psutil


class InventoryBuilder:
    def __init__(self):
        
        self.all_desktop_apps = {}
        self.folder_inventory = {}
        self.desktop_root = Path.home() / "Desktop"
        self.search_paths = [Path("/usr/share/applications"), Path.home() / ".local/share/applications", Path.home() / ".local/share/flatpak/exports/share/applications"]
            
        
    def CreateDesktopDatabase(self):
    ####create a global dictionary at first so we dont have to loop everytime
        for path in self.search_paths:
            if not path.exists():
                continue
            for desktop_file in path.glob("*.desktop"):
                try:
                    entry = DesktopEntry(str(desktop_file))
                    name = entry.getName()
                    
                    if not name:
                        continue
                    self.all_desktop_apps [name.lower()] = {"categories":entry.getCategories(),
                    "exec": entry.getExec(),
                    "desktop_file": str(desktop_file)
                    }
                except Exception:
                    pass
        return self.all_desktop_apps
        

    def Desktop_Directory_Apps(self):
        for folder in self.desktop_root.iterdir():
            if not folder.is_dir():
                continue
            self.folder_inventory[folder.name.lower()] = []
            
            for df in folder.glob("*.desktop"):
                try:
                    entry = DesktopEntry(str(df))
                    self.folder_inventory[folder.name.lower()].append(entry.getName())
                    
                except:
                    pass
        return self.folder_inventory