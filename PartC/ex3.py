from pathlib import Path
from xdg.DesktopEntry import DesktopEntry




def find_app(app_name):
	path = Path("/usr/share/applications")
	desktop_files = list(path.glob("*.desktop"))
	for i in desktop_files:
		entry = DesktopEntry(str(i))
		if str(entry.getName()) == app_name:
			return {"found": True, "cactegories":entry.getCategories()}
		


print(find_app("Appearance"))
print(find_app("Logout"))
print(find_app("firefox"))
			
	

