__author__ = "qiao"

"""
Simplified TrialGPT-Matching functions for researcher and grant matching.
"""

import json
from nltk.tokenize import sent_tokenize
import time
import os
import openai #import open ai instead of azure

openai.api_key = os.getenv("API_KEY")

def parse_criteria(criteria):
        """Utility to enumerate eligibility or objective text."""
        output = ""
        criteria = criteria.split("\n\n")

        idx = 0
        for criterion in criteria:
                criterion = criterion.strip()

                if len(criterion) < 5:
                        continue

                output += f"{idx}. {criterion}\n"
                idx += 1

        return output


def print_grant(grant_info: dict) -> str:
        """Return a formatted grant description string."""

        grant = f"Title: {grant_info['title']}\n"
        grant += f"Summary: {grant_info.get('summary', '')}\n"
        if 'eligibility' in grant_info:
                grant += "Eligibility:\n %s\n" % parse_criteria(grant_info['eligibility'])
        if 'objectives' in grant_info:
                grant += "Objectives:\n %s\n" % parse_criteria(grant_info['objectives'])

        return grant


def get_matching_prompt(
        grant_info: dict,
        researcher: str,
) -> str:
        """Create the matching prompt for a researcher and a grant."""

        prompt = (
                "You are a helpful assistant for research grant matching. Your task is to "
                "compare a researcher summary with the objectives or eligibility of a grant "
                "to assess fit. Briefly explain your reasoning and output a label from "
                "{'eligible', 'not eligible', 'unclear'}. "
                "Respond only with a JSON dict formatted as "
                "Dict{'reason': Str, 'label': Str}."
        )

        user_prompt = f"Here is the researcher summary:\n{researcher}\n\n"
        user_prompt += f"Here is the grant information:\n{print_grant(grant_info)}\n\n"
        user_prompt += "Plain JSON output:"

        return prompt, user_prompt


def trialgpt_matching(grant: dict, researcher: str, model: str):
        """Run the grant matching prompt and return the LLM output."""

        system_prompt, user_prompt = get_matching_prompt(grant, researcher)

        messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
        ]

        response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0,
        )

        message = response.choices[0].message.content.strip()
        message = message.strip("`").strip("json")

        try:
                results = json.loads(message)
        except Exception:
                results = {"output": message}

        return results
