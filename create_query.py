#import streamlit as st
import json


def create_jsonl_entry(patient_id, patient_narrative):
    """Creates a JSONL formatted string from patient data."""
    data = {
        "_id": patient_id,
        "text": patient_narrative,
        "metadata": {}
    }
    return json.dumps(data) + "\n"


def generate_jsonl_file(patient_id, patient_narrative):
    """Generates JSONL file content and returns it as bytes."""
    jsonl_content = create_jsonl_entry(patient_id, patient_narrative)
    return jsonl_content.encode("utf-8")


#st.title("Patient Narrative to JSONL Converter")

# User inputs
#patient_id = st.text_input("Enter Patient ID:")
#patient_narrative = st.text_area("Enter Patient Narrative:")

#if st.button("Generate JSONL and Download"):
#    if patient_id and patient_narrative:
#        jsonl_bytes = generate_jsonl_file(patient_id, patient_narrative)

#        st.download_button(
#            label="Download JSONL File",
#            data=jsonl_bytes,
#            file_name=f"{patient_id}.jsonl",
#            mime="application/json"
#        )
#    else:
#        st.warning("Please enter both Patient ID and Patient Narrative.")
