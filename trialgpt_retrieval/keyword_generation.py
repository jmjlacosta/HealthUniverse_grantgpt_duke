__author__ = "qiao"

"""
generate the search keywords for each patient
"""

import json
import os
import openai #import open ai instead of azure

import sys

openai.api_key = os.getenv("API_KEY")


def get_keyword_generation_messages(note):
	system = 'You are a helpful assistant and your task is to help search relevant clinical trials for a given patient description. Please first summarize the main medical problems of the patient. Then generate up to 32 key conditions for searching relevant clinical trials for this patient. The key condition list should be ranked by priority. Please output only a JSON dict formatted as Dict{{"summary": Str(summary), "conditions": List[Str(condition)]}}.'

	prompt =  f"Here is the patient description: \n{note}\n\nJSON output:"


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
