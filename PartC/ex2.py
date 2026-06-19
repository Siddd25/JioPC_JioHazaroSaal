from pathlib import Path
from xdg.DesktopEntry import DesktopEntry

path = Path("/usr/share/applications")

desktop_files = list(path.glob("*.desktop"))

for i in desktop_files[:20]:
	entry = DesktopEntry(str(i))
	print(f"{str(entry.getName())} -> {str(entry.getCategories())}")
	

