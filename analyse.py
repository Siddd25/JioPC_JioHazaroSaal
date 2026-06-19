
import os

from openai import OpenAI
from dotenv import load_dotenv

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

    def load_prompt(self):

        with open(
            "prompts/analyze_log.txt",
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

    def build_prompt(self, log_text):

        prompt_template = self.load_prompt()

        return f"""
{prompt_template}

TEST LOG:

{log_text}
"""

    def analyze(self, log_path):

        log_text = self.load_log(log_path)

        full_prompt = self.build_prompt(
            log_text
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

    args = parser.parse_args()

    analyzer = LogAnalyzer()

    result = analyzer.analyze(
        args.log
    )

    print(result)


if __name__ == "__main__":
    main()