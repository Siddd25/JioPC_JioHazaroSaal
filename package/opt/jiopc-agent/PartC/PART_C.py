from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml
import json
from datetime import datetime
import time



class PartCTester:

    def __init__(self,logger):
        self.total_time = time.perf_counter()


        self.passed = 0
        self.misplaced =0
        self.missing =0

        self.status =""
        self.detail = ""


        self.log_file = logger

        	
        


    def run(self,config_data, all_desktop_apps, desktop_folder_inventory):


        for test in config_data:
            start_time = time.perf_counter()
            app_name = test["name"]
            expected_category = test["expected_category"]
            expected_folder = test['expected_desktop_folder'].lower()
            
            app = self.find_app(app_name.lower(), all_desktop_apps)
            
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
                
            elif app_name.lower() not in [x.lower() for x in desktop_folder_inventory.get(expected_folder, [])]:
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
                "test_name": "App presence Testing",
                "app_name" : app_name,
                "result": status,
                "duration_ms": duration_ms,
                "detail_message": detail
            }
            self.log_file.log(record)

        final_summary = {
        "component":"C",
        "type":"summary",
        "TOTAL" : len(config_data),
        "PASS":self.passed,
        "MISPLACED":self.misplaced,
        "MISSING":self.missing
        }

        self.log_file.log(final_summary)
        #print("log file updated")
       
        total_duration = round((time.perf_counter() - self.total_time)*1000,4)
        #print(f"Total time taken for Part C analysis  is {total_duration}")

        return final_summary
                	


    def find_app(self, app_name, all_desktop_apps):
            if app_name in all_desktop_apps:
                return {"found" : True, **all_desktop_apps[app_name]}
            return {"found":False}







