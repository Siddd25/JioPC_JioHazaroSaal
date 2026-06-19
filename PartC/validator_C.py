from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml
import json
from datetime import datetime
import time


#build inventory
total_time = time.perf_counter()
all_desktop_apps = {}
folder_inventory = {}
desktop_root = Path.home() / "Desktop"

passed = 0
misplaced =0
missing =0


search_paths = [Path("/usr/share/applications"), Path.home() / ".local/share/applications"]


####create a global dictionary at first so we dont have to loop everytime
for path in search_paths:
	if not path.exists():
		continue
	for desktop_file in path.glob("*.desktop"):
		try:
			entry = DesktopEntry(str(desktop_file))
			name = entry.getName()
			
			if not name:
				continue
			all_desktop_apps [name.lower()] = {"categories":entry.getCategories(),
			"exec": entry.getExec(),
			"desktop_file": str(desktop_file)
			}
		except Exception:
			pass



for folder in desktop_root.iterdir():
	if not folder.is_dir():
		continue
	folder_inventory[folder.name.lower()] = []
	
	for df in folder.glob("*.desktop"):
		try:
			entry = DesktopEntry(str(df))
			folder_inventory[folder.name.lower()].append(entry.getName())
			
		except:
			pass	

print(folder_inventory)
def find_app(app_name):
	if app_name in all_desktop_apps:
		return {"found" : True, **all_desktop_apps[app_name]}
	return {"found":False}



log_file = open("partc_log.jsonl","w")
	
with open("config/tests.yaml") as f:
	data = yaml.safe_load(f)

status =""
detail = ""


for test in data['part C']:
	start_time = time.perf_counter()
	app_name = test["name"]
	expected_category = test["expected_category"]
	expected_folder = test['expected_folder'].lower()
	
	app = find_app(app_name.lower())
	
	if not app["found"]:
		#print(app_name, "MISSING",".desktop does not exist on System")
		status = "MISSING"
		detail = ".desktop does not exist on System"
		missing+=1
	
	elif expected_category.lower() not in [c.lower() for c in app["categories"]]: 
		#print(app_name, "MISPLACED","Wrong Category")
		status = "MISPLACED"
		detail = (
    f"Expected category={expected_category}, "
    f"Actual categories={app['categories']}"
)
		misplaced+=1
		
	elif app_name.lower() not in [x.lower() for x in folder_inventory.get(expected_folder, [])]:
		#print(app_name, "MISPLACED", "Wrong desktop shortcut folder")
		status = "MISPLACED"
		detail = (
    f"Expected folder={expected_folder}, "
    f"App not found in expected desktop folder"
)
		misplaced+=1
		
	else:
		#print(app_name, "PASSED", "Everything in place")
		status = "PASS"
		detail = "App exists in expected Category and expected Desktop Folder"
		passed+=1
		
	duration_ms = round((time.perf_counter() - start_time) * 1000,4)
        
        
	record = {
	    "timestamp": datetime.now().isoformat(),
	    "component": "C",
	    "test_name": app_name,
	    "result": status,
	    "duration_ms": duration_ms,
	    "detail_message": detail
	}
	log_file.write(json.dumps(record) + "\n")
	
			
print("\n **********SUMMARY**************")
print(f"passed:{passed}")
print(f"misplaced:{misplaced}")
print(f"missing:{missing}")

final_summary = {
  "timestamp": datetime.now().isoformat(),
  "component":"C",
  "type":"SUMMARY",
  "passed":passed,
  "misplaced":misplaced,
  "missing":missing
}

log_file.write(json.dumps(final_summary) + "\n")
print("log file updated")
log_file.close()
total_duration = round((time.perf_counter() - total_time)*1000,4)
print(f"Total time taken for Part C analysis  is {total_duration}")
