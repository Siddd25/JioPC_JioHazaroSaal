from utils.logger import CommonLogger
from PartA.PART_A import PartATester
from PartB.PART_B import PartBTester
from PartC.PART_C import PartCTester
from utils.inventory import InventoryBuilder

from pathlib import Path
from datetime import datetime

import argparse
import yaml
import time
import sys


class CoreRunner:

    def __init__(self, config_path):

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

    def run(self, part=None):

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

                    part_a_summary = parts["A"].run(
                        part_configs["A"]
                    )

                elif p == "B":

                    part_b_summary = parts["B"].run(
                        part_configs["B"], self.all_desktop_apps, self.desktop_folder_apps
                    )

                elif p == "C":

                    part_c_summary = parts["C"].run(
                        part_configs["C"], self.all_desktop_apps, self.desktop_folder_apps
                    )



            # print("Running Part A")
            # part_a_summary = part_a.run(
            #     self.config["web_apps"]
            # )

            # print("Running Part B")
            # part_b_summary = part_b.run(
            #     self.config["native_apps"]
            # )

            # print("Running Part C")
            # part_c_summary = part_c.run(
            #     self.config["desktop_presence"]
            # )

        elif part == "A":

            print("Running Part A")

            part_a_summary = parts["A"].run(
                part_configs["A"]
            )

        elif part == "B":

            print("Running Part B")

            part_b_summary = parts["B"].run(
                part_configs["B"], self.all_desktop_apps, self.desktop_folder_apps
            )

        elif part == "C":

            print("Running Part C")

            part_c_summary = parts["C"].run(
                part_configs["C"], self.all_desktop_apps, self.desktop_folder_apps
            )

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

        self.logger.log({
            "type": "SUMMARY",
            "total_runtime_sec": total_time
        })

        self.logger.close()
        print(
            f"Log file: {self.log_file_path}"
        )
        if total_failures == 0:
            print(f"All tests passed in {total_time}")
            print("EXIT_CODE=0")
            sys.exit(0)

        print("Some tests failed")
        print("EXIT_CODE=1")
        sys.exit(1)
        

        


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration"
    )

    parser.add_argument(
        "--part",
        choices=["A", "B", "C"],
        help="Run only a specific part"
    )

    args = parser.parse_args()

    runner = CoreRunner(
        args.config
    )

    runner.run(
        args.part
    )