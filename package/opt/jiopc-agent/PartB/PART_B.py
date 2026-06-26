from pathlib import Path
from xdg.DesktopEntry import DesktopEntry
import yaml
import os 
import signal
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
        
        

        self.PASS_B = 0
        self.DEGRADED_B=0
        self.FAIL_B = 0

        self.logger = logger



    def run(self, config_data, all_desktop_apps):

        for i in config_data:
            start_time = time.time()
            app_search_results = self.find_app(i['app_name'].lower(), all_desktop_apps)
            #print(app_search_results)

            if app_search_results["found"]:
                
                command = self.extract_exec(app_search_results["exec"])
               
                
                exact_executable = shutil.which(command[0])
               
                if exact_executable:
                    
                    #print(f"Appication Binary exists at {exact_executable}")
                    result = self.health_check(i['app_name'],command, float(i['launch_timeout_s']))
                    total_time = time.time() - start_time -2
                    result["test_name"] = "Native App Health Testing"
                    result ['executable_location'] = exact_executable
                    result['expected_desktop_file_location'] = i['desktop_file']
                    result['actual_desktop_file_location'] = app_search_results['desktop_file']

                    status = result["status"]

                    if status == "PASS":
                        self.PASS_B += 1
                    elif status == "FAIL":
                        self.FAIL_B += 1
                    elif status == "DEGRADED":
                        self.DEGRADED_B += 1
                    
                    
                else:
                    result = {"app_name":i['app_name'],"status" : "FAIL", 'expected_desktop_file_location':i['desktop_file'],'actual_desktop_file_location': app_search_results['desktop_file'],"detail":"executable not found"}
                    total_time = time.time() - start_time
                    self.FAIL_B +=1
                    
            else :
                result = {'app_name': i["app_name"],'expected_desktop_file_location':i['desktop_file'], "status" : "FAIL", 'detail':"App not found on system"} 
                total_time = time.time() - start_time
                self.FAIL_B+=1
            result['total_test_time_s'] = total_time
            
            result["timestamp"] = datetime.now().isoformat()
            result["component"] = "B"
            self.logger.log(result)	
            #print(result)
        summary = {'component' : 'B', "TOTAL": len(config_data), "PASS" : self.PASS_B, "FAIL": self.FAIL_B, "DEGRADED": self.DEGRADED_B}
        self.logger.log(summary)
        	
                
        return summary


   	

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
            # p = subprocess.Popen(command)
            p = subprocess.Popen(
            command,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
            
            
            # Wait until both process and window appear
            process_found = False
            window_found = False

            while time.time() - start < timeout:

                parent = psutil.Process(p.pid)

                valid_pids = {parent.pid}

                try:
                    for child in parent.children(recursive=True):
                        valid_pids.add(child.pid)
                except Exception:
                    pass

                if psutil.pid_exists(p.pid):
                    process_found = True

                try:
                    output = subprocess.check_output(
                        ["wmctrl", "-lp"]
                    ).decode(errors="ignore")

                    for line in output.splitlines():

                        parts = line.split()

                        if len(parts) < 5:
                            continue

                        try:
                            window_pid = int(parts[2])

                            if window_pid in valid_pids:

                              

                                window_found = True
                                break

                        except Exception:
                            pass
                                        
                    

                except Exception:
                    pass

                if process_found and window_found:
                    break

                time.sleep(0.5)
            
            launch_time_ms = round(
            (time.time() -start) * 1000,
            2
        )

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
                "launch_time_ms": launch_time_ms,
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

                try:

                    os.killpg(
                        os.getpgid(p.pid),
                        signal.SIGTERM
                    )

                    time.sleep(2)

                    try:
                        os.killpg(
                            os.getpgid(p.pid),
                            signal.SIGKILL
                        )
                    except ProcessLookupError:
                        pass

                except Exception:
                    pass

                # Cooldown before next test
                time.sleep(2)
                
            
  
    def find_app(self, app_name, all_desktop_apps):
        if app_name in all_desktop_apps:
            return {"found" : True, **all_desktop_apps[app_name]}
        return {"found":False}


    
		
	
	
