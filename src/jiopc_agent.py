from utils.logger import CommonLogger
from PartA.PART_A import PartATester
from PartB.PART_B import PartBTester
from PartC.PART_C import PartCTester
from utils.inventory import InventoryBuilder
from utils.email_sender import EmailSender
from pathlib import Path
from datetime import datetime
from analyse import LogAnalyzer
import argparse
import yaml
import time
import sys
import psutil
import os
import json
import threading

import re





class CoreRunner:

    def __init__(self, config_path):
        self.process = psutil.Process(os.getpid())
        self.process.cpu_percent(interval=None)


        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        log_dir = Path(
            self.config["test_agent"]["log_dir"]
        ).expanduser()

        log_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        


        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.log_file_path = (
            log_dir /
            f"test_run_{timestamp}.log"
        )

        self.logger = CommonLogger(
            self.log_file_path
        )

        self.inventory_builder = InventoryBuilder()
        self.all_desktop_apps = self.inventory_builder.CreateDesktopDatabase()
        self.desktop_folder_apps = self.inventory_builder.Desktop_Directory_Apps()

        
        self.peak_ram_mb = 0
        self.peak_cpu_percent =0
    
    def monitor_resources(self):

        while self.monitoring:

            ram_mb = (
                self.process.memory_info().rss
                / (1024 * 1024)
            )

            cpu = self.process.cpu_percent(interval=0.5)

            self.peak_ram_mb = max(
                self.peak_ram_mb,
                ram_mb
            )

            self.peak_cpu_percent = max(
                self.peak_cpu_percent,
                cpu
            )

         

    def run(self, part=None):
        self.monitoring = True

        monitor_thread = threading.Thread(
    target=self.monitor_resources,
    daemon=True
)

        monitor_thread.start()

        print("Test Agent is Running......")

        start_time = time.time()

       

        execution_order = self.config['test_agent']["execution_order"]

        parts = {"A": PartATester(self.logger), "B": PartBTester(self.logger), "C" : PartCTester(self.logger)}

        part_configs = {
        "A": self.config["web_apps"],
        "B": self.config["native_apps"],
        "C": self.config["desktop_presence"]
        }

        # part_a = PartATester(self.logger)
        # part_b = PartBTester(self.logger)
        # part_c = PartCTester(self.logger)

        part_a_summary = {}
        part_b_summary ={}
        part_c_summary ={}


      
        if part is None:
            for p in execution_order:
                if p == "A":
                    print("Running Part A")
                  
                    part_a_summary = parts["A"].run(
                        part_configs["A"]
                    )
                    #self.update_peak_ram()

                elif p == "B":
                    print("Running Part B")
                    part_b_summary = parts["B"].run(
                        part_configs["B"], self.all_desktop_apps)
                    #self.update_peak_ram()

                elif p == "C":
                    print("Running Part C")

                    part_c_summary = parts["C"].run(
                        part_configs["C"], self.all_desktop_apps, self.desktop_folder_apps
                    )
                    #self.update_peak_ram()


        elif part == "A":

            print("Running Part A")

            part_a_summary = parts["A"].run(
                part_configs["A"]
            )
            #self.update_peak_ram()

        elif part == "B":

            print("Running Part B")

            part_b_summary = parts["B"].run(
                part_configs["B"], self.all_desktop_apps
            )
            #self.update_peak_ram()

        elif part == "C":

            print("Running Part C")

            part_c_summary = parts["C"].run(
                part_configs["C"], self.all_desktop_apps,self.desktop_folder_apps
                    
            )
            #self.update_peak_ram()

        total_time = round(
            time.time() - start_time,
            2
        )
        total_failures = (
        part_a_summary.get("FAIL", 0)
        + part_b_summary.get("FAIL", 0)
        + part_c_summary.get("FAIL", 0)
    )

        total_failures += (
            part_a_summary.get("BLOCKED", 0)
            + part_b_summary.get("BLOCKED", 0)
        )

        total_failures += (
            part_b_summary.get("DEGRADED", 0)
            + part_c_summary.get("MISSING", 0)
            + part_c_summary.get("MISPLACED", 0)
        )

       

        final_summary = {
    "type": "FINAL_SUMMARY",
    "timestamp": datetime.now().isoformat(),
    "total_runtime_sec": total_time,

    "component_A": part_a_summary,
    "component_B": part_b_summary,
    "component_C": part_c_summary,

    "total_tests":
        part_a_summary.get("TOTAL", 0)
        + part_b_summary.get("TOTAL", 0)
        + part_c_summary.get("TOTAL", 0),

    "total_pass":
        part_a_summary.get("PASS", 0)
        + part_b_summary.get("PASS", 0)
        + part_c_summary.get("PASS", 0),

    "total_fail":
        part_a_summary.get("FAIL", 0)
        + part_b_summary.get("FAIL", 0),

    "total_blocked":
        part_a_summary.get("BLOCKED", 0),

    "total_degraded":
        part_b_summary.get("DEGRADED", 0),

    "total_missing":
        part_c_summary.get("MISSING", 0),

    "total_misplaced":
        part_c_summary.get("MISPLACED", 0)
}       
        self.logger.log(final_summary)


        self.monitoring = False
        monitor_thread.join(timeout=1)

      
        self.logger.log({
    "type": "RESOURCE_USAGE",
    "peak_agent_ram_mb": round(
        self.peak_ram_mb,
        2
    ), 
    "peak_agent_cpu_percent":round(self.peak_cpu_percent,2)
})
        

        self.logger.close()
        print(
            f"Log file: {self.log_file_path}"
        )
        if total_failures == 0:
            print(f"All tests passed in {total_time}")
            print("EXIT_CODE=0")
            return 0 

        print("Some tests failed")
        print("EXIT_CODE=1")
        return 1
    


        


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration",
        
    )

    parser.add_argument(
        "--part",
        choices=["A", "B", "C"],
        help="Run only a specific part"
    )

    parser.add_argument("--analyse", action="store_true")
    parser.add_argument("--email", help="Enter the recipent's email id")

    args = parser.parse_args()

    runner = CoreRunner(
        args.config
    )

    exit_code = runner.run(
        args.part
    )

    if args.analyse:
        analyzer = LogAnalyzer()
        executive_summary = analyzer.analyze(runner.log_file_path, args.config)
       

        analysis_file = (
        Path(runner.log_file_path)
        .with_suffix(".analysis.txt")
                    )
        
        
        print(executive_summary)
        with open(analysis_file, "w") as f:
            f.write(executive_summary)

   


        if args.email:

                sender = EmailSender(
                runner.config["email"], args.email
            )

                sender.send(
                    subject="[JioPC] Test Analysis Report",
                    body=executive_summary
                )
                print("Mail sent succesfully")



        print(
        f"Analysis saved to {analysis_file}"
        ) 
          

    sys.exit(exit_code)