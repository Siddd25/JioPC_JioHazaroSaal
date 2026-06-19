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
class PartBTester:
    def __init__(self,logger):
        self.total_time = time.perf_counter()
        self.all_desktop_apps = {}
        self.folder_inventory = {}
        self.desktop_root = Path.home() / "Desktop"
        self.search_paths = [Path("/usr/share/applications"), Path.home() / ".local/share/applications", Path.home() / ".local/share/flatpak/exports/share/applications"]
        
        

        self.PASS_B = 0
        self.DEGRADED_B=0
        self.FAIL_B = 0

        self.logger = logger



    def run(self, config_data):
               
     
        
        
        
        self.CreateDesktopDatabase()
        self.Desktop_Directory_Apps()


        for i in config_data:
            start_time = time.time()
            app_search_results = self.find_app(i['app_name'].lower())
            #print(app_search_results)

            if app_search_results["found"]:
                
                command = self.extract_exec(app_search_results["exec"])
                
                exact_executable = shutil.which(command[0])
                if exact_executable:
                    
                    #print(f"Appication Binary exists at {exact_executable}")
                    result = self.health_check(i['app_name'],command, float(i['timeout']))
                    total_time = time.time() - start_time
                    result ['executable_location'] = exact_executable
                    result['desktop_file'] = app_search_results['desktop_file']
                    status = result["status"]

                    if status == "PASS":
                        self.PASS_B += 1
                    elif status == "FAIL":
                        self.FAIL_B += 1
                    elif status == "DEGRADED":
                        self.DEGRADED_B += 1
                    
                    
                else:
                    result = {"app_name":i['app_name'],"status" : "FAIL", 'desktop_file': app_search_results['desktop_file'],"detail":"executable not found"}
                    total_time = time.time() - start_time
                    self.FAIL_B +=1
                    
            else :
                result = {'app_name': i["app_name"], "status" : "FAIL", 'detail':"App not found on system"} 
                total_time = time.time() - start_time
                self.FAIL_B+=1
            result['total_time'] = total_time
            
            result["timestamp"] = datetime.now().isoformat()
            result["component"] = "B"
            self.logger.log(result)	
            #print(result)
        summary = {'COMPONENT' : 'B', "TOTAL": len(config_data), "PASS" : self.PASS_B, "FAIL": self.FAIL_B, "DEGRADED": self.DEGRADED_B}
        self.logger.log(summary)
        	
                
        return summary


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

    def extract_exec(self, raw):
        result = []
        for i in raw.split():
            if i.startswith("%"):
                continue
            result.append(i)
        return result
        



    def health_check(self, app_name, command, timeout):

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

            #print("Application window opened successfully")

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
                
            
  
    def find_app(self, app_name):
        if app_name in self.all_desktop_apps:
            return {"found" : True, **self.all_desktop_apps[app_name]}
        return {"found":False}


    
		
	
	
