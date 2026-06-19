from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml
import json
from datetime import datetime
import time



class PartCTester:

    def __init__(self,logger):
        self.total_time = time.perf_counter()
        self.all_desktop_apps = {}
        self.folder_inventory = {}
        self.desktop_root = Path.home() / "Desktop"

        self.passed = 0
        self.misplaced =0
        self.missing =0

        self.status =""
        self.detail = ""


        self.search_paths = [Path("/usr/share/applications"), Path.home() / ".local/share/applications"]
        self.log_file = logger

        	
        


    def run(self,config_data):
     

           
        self.CreateDesktopDatabase()
        self.Desktop_Directory_Apps()

        for test in config_data:
            start_time = time.perf_counter()
            app_name = test["name"]
            expected_category = test["expected_category"]
            expected_folder = test['expected_folder'].lower()
            
            app = self.find_app(app_name.lower())
            
            if not app["found"]:
                #print(app_name, "MISSING",".desktop does not exist on System")
                status = "MISSING"
                detail = ".desktop does not exist on System"
                self.missing+=1
            
            elif expected_category.lower() not in [c.lower() for c in app["categories"]]: 
                #print(app_name, "MISPLACED","Wrong Category")
                status = "MISPLACED"
                detail = (
            f"Expected category={expected_category}, "
            f"Actual categories={app['categories']}"
        )
                self.misplaced+=1
                
            elif app_name.lower() not in [x.lower() for x in self.folder_inventory.get(expected_folder, [])]:
                #print(app_name, "MISPLACED", "Wrong desktop shortcut folder")
                status = "MISPLACED"
                detail = (
            f"Expected folder={expected_folder}, "
            f"App not found in expected desktop folder"
        )
                self.misplaced+=1
                
            else:
                #print(app_name, "PASSED", "Everything in place")
                status = "PASS"
                detail = "App exists in expected Category and expected Desktop Folder"
                self.passed+=1
                
            duration_ms = round((time.perf_counter() - start_time) * 1000,4)
                
                
            record = {
                "timestamp": datetime.now().isoformat(),
                "component": "C",
                "test_name": app_name,
                "result": status,
                "duration_ms": duration_ms,
                "detail_message": detail
            }
            self.log_file.log(record)

        final_summary = {
        "timestamp": datetime.now().isoformat(),
        "component":"C",
        "type":"SUMMARY",
        "passed":self.passed,
        "misplaced":self.misplaced,
        "missing":self.missing
        }

        self.log_file.log(final_summary)
        #print("log file updated")
       
        total_duration = round((time.perf_counter() - self.total_time)*1000,4)
        #print(f"Total time taken for Part C analysis  is {total_duration}")

        return final_summary
                


    ####create a global dictionary at first so we dont have to loop everytime
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


    def find_app(self, app_name):
            if app_name in self.all_desktop_apps:
                return {"found" : True, **self.all_desktop_apps[app_name]}
            return {"found":False}







