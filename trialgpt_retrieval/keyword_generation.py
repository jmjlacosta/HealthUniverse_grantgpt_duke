__author__ = "qiao"

"""
Generate search keywords for each researcher profile.
"""

import json
import os
import openai #import open ai instead of azure

import sys

openai.api_key = os.getenv("API_KEY")


def get_keyword_generation_messages(profile):
        system = (
            'You are a helpful assistant and your task is to help search relevant '
            'grants for a given researcher profile. Please first summarize the main '
            'research interests and expertise. Then generate up to 32 key research '
            'topics for searching relevant grants for this researcher. The key topic '
            'list should be ranked by priority. Please output only a JSON dict formatted '
            'as Dict{"summary": Str(summary), "keywords": List[Str(keyword)]}}.'
        )

        prompt =  f"Here is the researcher profile: \n{profile}\n\nJSON output:"


	messages = [
		{"role": "system", "content": system},
		{"role": "user", "content": prompt}
	]
	
	return messages


if __name__ == "__main__":
	# the corpus: trec_2021, trec_2022, or sigir
	#corpus = sys.argv[1]

	# the model index to use
	model = "gpt-4o"#sys.argv[2]

	outputs = {}
	
	with open(f"dataset/data/queries.jsonl", "r") as f:
		for line in f.readlines():
			entry = json.loads(line)
			messages = get_keyword_generation_messages(entry["text"])

			response = openai.ChatCompletion.create(
				model=model,
				messages=messages,
				temperature=0,
			)

			output = response.choices[0].message.content
			output = output.strip("`").strip("json")
			
			outputs[entry["_id"]] = json.loads(output)

			with open(f"dataset/data/id2queries.json", "w") as f:
				json.dump(outputs, f, indent=4)
