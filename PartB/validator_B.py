from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml
import json
from datetime import datetime
import time
import shutil
import subprocess
import psutil

#build inventory
total_time = time.perf_counter()
all_desktop_apps = {}
folder_inventory = {}
desktop_root = Path.home() / "Desktop"

PASS_B = 0
DEGRADED_B=0
FAIL_B =0


search_paths = [Path("/usr/share/applications"), Path.home() / ".local/share/applications", Path.home() / ".local/share/flatpak/exports/share/applications"]


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

def extract_exec(raw):
	result = []
	for i in raw.split():
		if i.startswith("%"):
			continue
		result.append(i)
	return result
	

# def health_check(app_name,exact_executable, timeout):
	
# 	start = time.time()
# 	try:
	
# 		p = subprocess.Popen(exact_executable)
# 		time.sleep(2)
# 		output = subprocess.check_output(["wmctrl", "-lp"]).decode()

# 		if expected_process_name.lower() not in output.lower():
# 			return {
# 			"app_name": app_name,
# 			"status": "FAIL",
# 			"detail": "Application window failed to open"}
		

# 		else:
# 			print("Application window opened successfully")	

# 	except Exception as e:
# 		print(f"Unable to open application : {e}")
# 		return {
#     "app_name": app_name,
#     "status": "FAIL",
#     "detail": str(e)}
	

# 	while time.time() - start < timeout:
# 		if psutil.pid_exists(p.pid):
#         		break

# 		time.sleep(0.1)

# 	else:
# 		return {
# 		"app_name": app_name,
#         	"status":"FAIL",
#         	"detail":"Process did not appear within timeout"
#     			}
	
# 	#print(psutil.pid_exists(p.pid))
	
# 	for _ in range(50):

#         	if p.poll() is not None:
#             		return {
#             	"app_name": app_name,
#                 "status": "DEGRADED",
#                 "detail": "Process terminated before health check completed"
#             		}

#         	time.sleep(0.1)
# 	try:
# 		process = psutil.Process(p.pid)
# 		process_name = process.name()
		

# 		rss_mb = process.memory_info().rss / (1024 * 1024)

# 		# CPU measurement
# 		process.cpu_percent()
# 		time.sleep(1)

# 		cpu = process.cpu_percent()

# 		result = {
# 		    "actual_process_name" : process_name,
# 		    "app_name" : app_name,
# 		    "status": "PASS",
# 		    "rss_mb": round(rss_mb, 2),
# 		    "cpu_percent": cpu
# 		}

# 	except psutil.NoSuchProcess:
		
# 		result = {
#     		    "actual_process_name" : process_name,
#     		    "app_name" : app_name,
# 		    "status": "DEGRADED",
# 		    "detail": "Process disappeared during metric collection"
# 		}
		

#     # Clean shutdown
# 	try:
# 		parent = psutil.Process(p.pid)

# 		for child in parent.children(recursive=True):
# 			child.kill()

# 		parent.kill()

# 	except Exception:
# 		pass

# 	return result

def health_check(app_name, command, timeout):

    p = None

    try:
        start = time.time()

        # Launch application
        p = subprocess.Popen(command)

        # Wait until both process and window appear
        process_found = False
        window_found = False

        while time.time() - start < timeout:

            if psutil.pid_exists(p.pid):
                process_found = True

            try:
                output = subprocess.check_output(
                    ["wmctrl", "-lp"]
                ).decode(errors="ignore")
                
                for app_name_token in app_name.lower().split():
                    if app_name_token in output.lower():
                        window_found = True
                        break

            except Exception:
                pass

            if process_found and window_found:
                break

            time.sleep(0.5)

        if not process_found:
            return {
                "app_name": app_name,
                "status": "FAIL",
                "detail": f"Process did not appear within {timeout}s"
            }

        if not window_found:
            return {
                "app_name": app_name,
                "status": "FAIL",
                "detail": f"Window did not appear within {timeout}s"
            }

        print("Application window opened successfully")

        # Verify it stays alive for 5 seconds
        for _ in range(50):

            if p.poll() is not None:
                return {
                    "app_name": app_name,
                    "status": "DEGRADED",
                    "detail": "Process terminated before health check completed"
                }

            time.sleep(0.1)

        process = psutil.Process(p.pid)

        rss_mb = process.memory_info().rss / (1024 * 1024)

        # Capture CPU usage at T+5 seconds
        process.cpu_percent()
        time.sleep(1)
        cpu = process.cpu_percent()

        return {
            "app_name": app_name,
            "actual_process_name": process.name(),
            "window_detected": True,
            "status": "PASS",
            "rss_mb": round(rss_mb, 2),
            "cpu_percent": cpu
        }

    except psutil.NoSuchProcess:

        return {
            "app_name": app_name,
            "status": "DEGRADED",
            "detail": "Process disappeared during metric collection"
        }

    except Exception as e:

        return {
            "app_name": app_name,
            "status": "FAIL",
            "detail": str(e)
        }

    finally:

        if p is not None:

            # Close window politely
            try:
                subprocess.run(
                    ["wmctrl", "-c", app_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(1)
            except Exception:
                pass

            # Kill launcher + children
            try:
                parent = psutil.Process(p.pid)

                children = parent.children(recursive=True)

                for child in children:
                    try:
                        child.terminate()
                    except Exception:
                        pass

                try:
                    parent.terminate()
                except Exception:
                    pass

                gone, alive = psutil.wait_procs(
                    children + [parent],
                    timeout=3
                )

                for proc in alive:
                    try:
                        proc.kill()
                    except Exception:
                        pass

            except Exception:
                pass
        	
        	
	
	
	
with open("config/test.yaml") as f:
	data = yaml.safe_load(f)
      



log_file = open("partb_log.jsonl","w")		

#test_app = "Audacious"
def find_app(app_name):
	if app_name in all_desktop_apps:
		return {"found" : True, **all_desktop_apps[app_name]}
	return {"found":False}


for i in data["PartB"]:
	start_time = time.time()
	app_search_results = find_app(i['app_name'].lower())
	print(app_search_results)

	if app_search_results["found"]:
		
		command = extract_exec(app_search_results["exec"])
		
		exact_executable = shutil.which(command[0])
		if exact_executable:
			
			print(f"Appication Binary exists at {exact_executable}")
			result = health_check(i['app_name'],command, float(i['timeout']))
			total_time = time.time() - start_time
			result ['executable_location'] = exact_executable
			result['desktop_file'] = app_search_results['desktop_file']
			status = result["status"]

			if status == "PASS":
			    PASS_B += 1
			elif status == "FAIL":
			    FAIL_B += 1
			elif status == "DEGRADED":
			    DEGRADED_B += 1
			
			
		else:
			result = {"app_name":i['app_name'],"status" : "FAIL", 'desktop_file': app_search_results['desktop_file'],"detail":"executable not found"}
			total_time = time.time() - start_time
			FAIL_B +=1
			
	else :
		result = {'app_name': i["app_name"], "status" : "FAIL", 'detail':"App not found on system"} 
		total_time = time.time() - start_time
		FAIL_B+=1
	result['total_time'] = total_time
	
	result["timestamp"] = datetime.now().isoformat()
	result["component"] = "B"
	log_file.write(json.dumps(result) + "\n")	
	print(result)
summary = {'part' : 'B', "TOTAL": len(data["PartB"]), "PASS" : PASS_B, "FAIL":FAIL_B, "DEGRADED": DEGRADED_B}
log_file.write(json.dumps(summary) + "\n")
log_file.close()		
		
		
		
	
	
