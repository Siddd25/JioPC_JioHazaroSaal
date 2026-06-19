from xdg.DesktopEntry import DesktopEntry
from pathlib import Path

name = "SMTube"
expected_category = "AudioVideo"

search_paths = ["/usr/share/applications","~/.local/share/applications"]
flag = 0
for i in search_paths:
	desktop_files = Path(i).glob("*desktop")
	for j in desktop_files:
		entry = DesktopEntry(j)
		if str(entry.getName()) == name:
			print("found")
			flag =1
			break

if flag == 0:
	print("Not found")

			

