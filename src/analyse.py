
import os

from openai import OpenAI
from dotenv import load_dotenv
import yaml
from pathlib import Path
from pathlib import Path
from utils.email_sender import EmailSender

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_CONFIG = PROJECT_ROOT / "jiopc-agent.yaml"

import argparse





class LogAnalyzer:

    def __init__(self):

        load_dotenv()

        self.base_url = os.getenv("LLM_BASE_URL")
        self.model = os.getenv("LLM_MODEL")
        self.api_key = os.getenv("LLM_API_KEY")

        self.validate_config()

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def validate_config(self):

        missing = []

        if not self.base_url:
            missing.append("LLM_BASE_URL")

        if not self.model:
            missing.append("LLM_MODEL")

        if not self.api_key:
            missing.append("LLM_API_KEY")

        if missing:
            raise ValueError(
                f"Missing environment variables: {', '.join(missing)}"
            )

    def load_prompt(self, prompt_file):

        with open(
            prompt_file,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    def load_log(self, log_path):

        with open(
            log_path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()

    def build_prompt(self, log_text, prompt_file):

        prompt_template = self.load_prompt(prompt_file)

        return f"""
{prompt_template}

TEST LOG:

{log_text}
"""

    def analyze(self, log_path, config_path):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        
        log_text = self.load_log(log_path)
        config_path = Path(config_path).resolve() 

        prompt_path = (
        config_path.parent /
        config["analysis"]["prompt_file_path"]
    ).resolve()

        full_prompt = self.build_prompt(
            log_text, prompt_path
        )

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )

        return response.choices[0].message.content


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--log",
        required=True,
        help="Path to log file"
    )

    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    

    args = parser.parse_args()

    analyzer = LogAnalyzer()

    result = analyzer.analyze(
        args.log, args.config
    )

    print(result)


    analysis_file = (
    Path(args.log)
    .with_suffix(".analysis.txt")
                )

    with open(analysis_file, "w") as f:
        f.write(result)

    print(
    f"Analysis saved to {analysis_file}"
    ) 
   
 


if __name__ == "__main__":
    main()