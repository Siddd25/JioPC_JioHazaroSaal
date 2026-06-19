from pathlib import Path
from xdg.DesktopEntry import DesktopEntry

folder_inventory = {}

desktop_root = Path.home() / "Desktop"

for folder in desktop_root.iterdir():
	if not folder.is_dir():
		continue
	folder_inventory[folder.name] = []
	
	for df in folder.glob("*.desktop"):
		try:
			entry = DesktopEntry(str(df))
			folder_inventory[folder.name].append(entry.getName())
			
		except:
			pass
print(folder_inventory)
