from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml


#build inventory

all_desktop_apps = {}
education_apps={}

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
			all_desktop_apps [name] = {"categories":entry.getCategories(),
			"exec": entry.getExec(),
			"desktop_file": str(desktop_file)
			}
		except Exception:
			pass

education_folder = Path.home() / "Desktop" / "Education"

for df in education_folder.glob("*.desktop"):
	entry = DesktopEntry(str(df))
	
	education_apps[entry.getName()] = {"categories":entry.getCategories(),
			"exec": entry.getExec(),
			"desktop_file": str(desktop_file)
			}
print(education_apps)	

def find_app(app_name):
	if app_name in all_desktop_apps:
		return {"found" : True, **all_desktop_apps[app_name]}
	return {"found":False}
	
with open("config/tests.yaml") as f:
	data = yaml.safe_load(f)

for test in data['desktop_presence']:
	app_name = test["name"]
	expected_category = test["expected_category"]
	expected_folder = test['expected_folder']
	
	app = find_app(app_name)
	
	if not app["found"]:
		print(app_name, "MISSING",".desktop does not exist on System")
	elif expected_category in app["categories"] and app_name in education_apps.keys():
		print(app_name, "PASSED","Everything in place")
	else:
		print(app_name, "MISPLACED", "wrong folder or Category")
