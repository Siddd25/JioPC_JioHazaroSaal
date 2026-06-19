from pathlib import Path
from xdg.DesktopEntry import DesktopEntry



#build inventory

all_desktop_apps = {}

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
print(len(all_desktop_apps))

print(all_desktop_apps["Appearance"])


def find_app(app_name):
	if app_name in all_desktop_apps:
		return {"found" : True, **all_desktop_apps[app_name]}
	return {"found":False}
	
	
print(find_app("Wi-Fi"))
