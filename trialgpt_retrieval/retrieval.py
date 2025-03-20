import json

# File paths
queries_file = "dataset/data/queries.jsonl"
corpus_file = "dataset/data/corpus.jsonl"
qid2nctids_results_file = "dataset/data/qid2nctids_results.json"
output_file = "dataset/data/retrieved_trials.json"

# Load queries.jsonl (line by line)
with open(queries_file, "r") as f:
    queries_data = {
        json.loads(line)['_id']: {'text': json.loads(line)['text']}
        for line in f
    }

# Load corpus.jsonl (line by line)
with open(corpus_file, "r") as f:
    corpus_data = {
        json.loads(line)['_id']: {
            k: json.loads(line)[k] for k in json.loads(line) if k != '_id'
        }
        for line in f
    }

# Load qid2nctids_results.json (full JSON file)
with open(qid2nctids_results_file, "r") as f:
    qid2nctids_results = json.load(f)

# Process retrieved trials
retrieved_trials = []

for patient in qid2nctids_results:
    if patient in queries_data:
        print(patient)  # Debugging: See which patient is processed
        valid_nctids = []
        
        for nctid in qid2nctids_results[patient]:
            if nctid in corpus_data:
                nctid_metadata = corpus_data[nctid]['metadata']
                nctid_metadata['NCTID'] = nctid
                valid_nctids.append(nctid_metadata)

        patient_retrieved_trial = {
            "patient_id": patient,
            "patient": queries_data[patient]['text'],
            "0": valid_nctids
        }
        retrieved_trials.append(patient_retrieved_trial)

# Save results to retrieved_trials.json
with open(output_file, "w") as f:
    json.dump(retrieved_trials, f, indent=4)

print(f"Results saved to {output_file}")
