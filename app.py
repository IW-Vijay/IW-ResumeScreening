import streamlit as st
import os
import base64
import requests
import uuid
import json


from dotenv import load_dotenv

from database_ops_utils import insert_job_description,insert_candidate_details, fetch_all_job_descriptions, fetch_all_candidates, fetch_matchings, calculate_overall_score, insert_matching
from langflow_utils import attach_files, match_section, generate_question, parse_questions


# Directory to store uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# API URL
RESUME_API_URL = "http://localhost:3000/api/v1/prediction/84f06a5d-b268-4ee8-adfc-c008273087e7"
JD_API_URL = "http://localhost:3000/api/v1/prediction/3cfbf8ea-e481-4d9a-a6d8-de441c65187a"
MACTHER_API_URL = "http://localhost:3000/api/v1/prediction/c6ed0476-4ee0-4d1a-840b-082f7364d57a" #without func calling
#MACTHER_API_URL = "http://localhost:3000/api/v1/prediction/407c4453-56bb-4f93-8b78-15d1722ff8eb" #with func calling
QUESTIONGENERATION_API_URL = "http://localhost:3000/api/v1/prediction/d8166d3c-6f79-4518-9c86-37dca4a5c115"
bearer_token = "aW8IQI_KyF0m9JmoNeQww8Pmj_2bg5ydT-maQATinvg"



# Load environment variables from .env file
load_dotenv()
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB_NAME"),
    "user": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "localhost",
    "port": 5432
}

# Helper function to save uploaded files
def save_uploaded_file(uploaded_file, folder):
    folder_path = os.path.join(UPLOAD_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# Helper function to encode file to base64
def encode_file_to_base64(file_path):
    with open(file_path, "rb") as f:
        encoded_data = base64.b64encode(f.read()).decode("utf-8")
    return encoded_data



# Helper function to query the API
def query_api(API_URL,chat_id,question, uploaded_file):
    headers = {"Authorization": "Bearer aW8IQI_KyF0m9JmoNeQww8Pmj_2bg5ydT-maQATinvg"}
    payload = {
        "question": question,
        "chatId": f"{chat_id}",
        "uploads": [
            {
                "data": f"data:text/plain;base64,{uploaded_file['content']}",
                "type": "file:full",
                "name": uploaded_file['name'],
                "mime": uploaded_file['mimeType']
            }
        ]
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def main():
    st.title("Candidate-Job Matching App")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Candidates", "Jobs", "Matching"])

    if page == "Candidates":
        st.header("Upload Candidate Resumes")
        uploaded_files = st.file_uploader("Upload Candidate PDFs", type=["pdf"], accept_multiple_files=True)

        if uploaded_files:
            st.subheader("Processing Uploaded Files:")
            for file in uploaded_files:
                if file.type != "application/pdf":
                    st.error(f"❌ {file.name} is not a PDF. Only PDF files are allowed.")
                    continue
                
                # Save the file locally
                file_path = save_uploaded_file(file, "candidates")
                #st.write(f"{file_path}")
                st.write(f"✔️ {file.name} saved successfully.")

                # Generate a random UUID
                chat_id = uuid.uuid4()
                print(chat_id)
                # Get file data for payload
                file = attach_files("84f06a5d-b268-4ee8-adfc-c008273087e7", chat_id, [file_path], bearer_token)

                # Send file to the API
                st.write("🔄 Sending file to API...")
                try:
                    api_response = query_api(RESUME_API_URL,chat_id,"Analyze the given resume.",file[0])
                    st.write("✅")
                    #st.json(api_response)
                    #raw_text = api_response["text"]
                    #clean_json_string = raw_text.replace("```json", "").replace("```", "").strip()
                    #parsed_data = json.loads(clean_json_string)

                    #st.json(parsed_data)
                    insert_candidate_details(api_response["usedTools"][0]["toolInput"])
                except Exception as e:
                    st.error(f"❌ Failed to query API: {str(e)}")

        # Retrieve all entries from the database
        st.subheader("All Candidates")
        try:
            candidates = fetch_all_candidates()

            if candidates:
                # Display Name and Created Date with Details Button
                for candidate in candidates:
                    col1, col2, col3 = st.columns([3, 3, 1])  # Columns for layout

                    # Show Name and Created Date
                    col1.write(f"**{candidate['candidate_name']}**")
                    col2.write(f"📅 {candidate['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")

                    # Add Details Button
                    if col3.button("Details", key=f"details-{candidate['candidate_id']}"):
                        # Open a sidebar with job details
                        with st.sidebar:
                            st.subheader(f"Details for {candidate['candidate_name']}")
                            st.write("### Basic Information")
                            st.write(f"**Name:** {candidate['candidate_name']}")
                            st.write(f"**Phone Number:** {candidate['phone_number']}")
                            st.write(f"**Email:** {candidate['email']}")

                            st.write("### Education")
                            st.write(f"**Degree:** {candidate['degree']}")

                            st.write("### Experience")
                            st.write(candidate['experience'])

                            st.write("### Responsibilities")
                            st.write(candidate['responsibility'])

                            st.write("### Technical Skills")
                            st.write(candidate['technical_skill'])

                            st.write("### Soft Skills")
                            st.write(candidate['soft_skill'])

                            st.write("### Certifications")
                            st.write(candidate['certificate'])

                            st.write("### Portfolios")
                            st.write(candidate['portfolios'])

                            st.write("### Additional Details")
                            st.write(f"**Years of Experience:** {candidate['yoe']} years")
                            st.write(f"**Profile Created At:** {candidate['created_at']}")
            else:
                st.info("No candidates found in the database.")

        except Exception as e:
            st.error(f"❌ Failed to fetch data from the database: {str(e)}")

    elif page == "Jobs":
        st.header("Upload Job Descriptions")
        uploaded_files = st.file_uploader("Upload Job PDFs", type=["pdf"], accept_multiple_files=True)

        if uploaded_files:
            st.subheader("Processing Uploaded Files:")
            for file in uploaded_files:
                if file.type != "application/pdf":
                    st.error(f"❌ {file.name} is not a PDF. Only PDF files are allowed.")
                    continue
                
                # Save the file locally
                file_path = save_uploaded_file(file, "jobs")
                st.write(f"✔️ {file.name} saved successfully.")

                # Generate a random UUID
                chat_id = uuid.uuid4()
                print(chat_id)
                # Get file data for payload
                file = attach_files("3cfbf8ea-e481-4d9a-a6d8-de441c65187a", chat_id, [file_path], bearer_token)
                
                # Send file to the API
                st.write("🔄 Sending file to API...")
                try:
                    api_response = query_api(JD_API_URL,chat_id,"Analyze the given job description.",file[0])
                    st.write("✅")
                    #raw_text = api_response["text"]
                    #clean_json_string = raw_text.replace("```json", "").replace("```", "").strip()
                    #parsed_data = json.loads(clean_json_string)
                    #st.json(api_response)
                    #st.json(api_response["usedTools"][0]["toolInput"])
                    insert_job_description(api_response["usedTools"][0]["toolInput"])
                except Exception as e:
                    st.error(f"❌ Failed to query API: {str(e)}")
        # Retrieve all entries from the database
        st.subheader("All Job Descriptions")
        try:
            job_descriptions = fetch_all_job_descriptions()

            if job_descriptions:
                # Display Name and Created Date with Details Button
                for job in job_descriptions:
                    col1, col2, col3 = st.columns([3, 3, 1])  # Columns for layout

                    # Show Name and Created Date
                    col1.write(f"**{job['name']}**")
                    col2.write(f"📅 {job['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")

                    # Add Details Button
                    if col3.button("Details", key=f"details-{job['job_id']}"):
                        # Open a sidebar with job details
                        with st.sidebar:
                            st.subheader(f"Details for {job['name']}")
                            st.write("### Degree")
                            st.write(job['degree'])
                            st.write("### Years of experience")
                            st.write(job['yoe'])
                            st.write("### Experience")
                            st.write(job['experience'])
                            st.write("### Technical Skills")
                            st.write(job['technical_skill'])
                            st.write("### Responsibility")
                            st.write(job['responsibility'])
                            st.write("### Soft Skills")
                            st.write(job['soft_skill'])
                            st.write("### Certifications")
                            st.write(job['certificate'])
            else:
                st.info("No job descriptions found in the database.")

        except Exception as e:
            st.error(f"❌ Failed to fetch data from the database: {str(e)}")

    elif page == "Matching":
        st.header("Match Candidates to Jobs")

        # Fetch job descriptions from the database
        try:
            job_descriptions = fetch_all_job_descriptions()

            if job_descriptions:
                # Job dropdown (initially no job selected)
                job_names = ["Select a Job"] + [job['name'] for job in job_descriptions]
                selected_job = st.selectbox("Select a Job to Match Candidates", job_names)

                if selected_job == "Select a Job":
                    st.info("Please select a job to proceed.")
                    selected_job = None
                # else:
                #     st.write(f"Selected Job: `{selected_job}`")
            else:
                st.write("No job descriptions found in the database.")

        except Exception as e:
            st.error(f"❌ Failed to fetch job descriptions from the database: {str(e)}")

        # Match button
        match_button_clicked = st.button("Match")

        # Fetch candidates and existing matchings
        try:
            candidates = fetch_all_candidates()
            if selected_job:
                selected_job_details = next(
                    job for job in job_descriptions if job['name'] == selected_job
                )
                job_id = selected_job_details["job_id"]

                # Fetch existing matchings for the selected job
                existing_matchings = fetch_matchings(job_id)

                if candidates:
                    st.subheader("Candidates")
                    pending_candidates = []  # List of candidates to process for matching

                    # Iterate over candidates and build a table with details
                    for candidate in candidates:
                        candidate_id = candidate["candidate_id"]
                        # Check if this candidate already has a matching entry
                        matching_entry = next(
                            (m for m in existing_matchings if m["candidate_id"] == candidate_id),
                            None,
                        )

                        # Determine matching status
                        status = "Matched" if matching_entry else "Pending"
                        match_score = matching_entry.get("matching_score", "N/A") if matching_entry else "N/A"

                        # Show a details button for each candidate
                        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                        with col1:
                            st.write(candidate["candidate_name"])
                        with col2:
                            st.write(status)
                        with col3:
                            st.write(match_score)
                        with col4:
                            details_button = st.button(f"Details", key=f"details_{candidate_id}")
                        with col5:
                            generate_question_button = st.button(f"Generate Questions", key=f"enerate_question_{candidate_id}")

                        if details_button and matching_entry:
                            # Fetch and display details from matchings
                            st.sidebar.subheader(f"Details for {candidate['candidate_name']}")
                            st.sidebar.write(f"**Match Score:** {match_score}")
                            st.sidebar.write(f"**Degree/Education**")
                            st.sidebar.write(f"**Score:** {matching_entry.get('education_score', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write(f"**Justification:** {matching_entry.get('education_comment', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write("---")
                            st.sidebar.write(f"**Experience**")
                            st.sidebar.write(f"**Score:** {matching_entry.get('experience_score', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write(f"**Justification:** {matching_entry.get('experience_comment', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write("---")
                            st.sidebar.write(f"**Responsibility**")
                            st.sidebar.write(f"**Score:** {matching_entry.get('responsibilitie_score', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write(f"**Justification:** {matching_entry.get('responsibilitie_comment', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write("---")
                            st.sidebar.write(f"**Technical Skills**")
                            st.sidebar.write(f"**Score:** {matching_entry.get('technicall_skills_score', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write(f"**Justification:** {matching_entry.get('technicall_skills_comment', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write("---")
                            st.sidebar.write(f"**Soft Skills**")
                            st.sidebar.write(f"**Score:** {matching_entry.get('soft_skills_score', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write(f"**Justification:** {matching_entry.get('soft_skills_comment', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write("---")
                            st.sidebar.write(f"**Certificates**")
                            st.sidebar.write(f"**Score:** {matching_entry.get('certificates_score', 'N/A') if matching_entry else 'N/A'}")
                            st.sidebar.write(f"**Justification:** {matching_entry.get('certificates_comment', 'N/A') if matching_entry else 'N/A'}")
                        if generate_question_button and matching_entry:
                            st.sidebar.subheader(f"Questions for {candidate['candidate_name']}")
                            data_for_questions = [candidate['experience'], candidate['technical_skill'], candidate['responsibility'], candidate['certificate']]
                            
                            spinner_placeholder = st.sidebar.empty()
                            spinner_placeholder.write("Generating questions...")
                            questions = generate_question(QUESTIONGENERATION_API_URL, bearer_token, data_for_questions)
                            spinner_placeholder.empty()

                            parsed_questions = parse_questions(questions["json"])
                            #st.sidebar.write(parsed_questions)
                            for category, category_questions in parsed_questions.items():
                                st.sidebar.write(f"**{category.capitalize()}**")
                                for idx, question in enumerate(category_questions, 1):
                                    st.sidebar.write(f"{idx}. {question}")
                                st.sidebar.write("---")


                        # Append pending candidates for matching logic
                        if not matching_entry:
                            pending_candidates.append(candidate)

                    # Perform matching for pending candidates
                    if match_button_clicked:
                        if not selected_job:
                            st.error("Please select a job to match candidates.")
                        elif not pending_candidates:
                            st.info("All candidates are already matched.")
                        else:
                            st.subheader("Matching Results")
                            matching_results = []
                            for candidate in pending_candidates:
                                # Example matching logic
                                education_match = match_section(MACTHER_API_URL, bearer_token, "Education", selected_job_details['degree'], candidate['degree'])
                                experience_match = match_section(MACTHER_API_URL, bearer_token, "Experience", selected_job_details['experience'], candidate['experience'])
                                responsibility_match = match_section(MACTHER_API_URL, bearer_token, "Responsibilities", selected_job_details['responsibility'], candidate['responsibility'])
                                technical_skill_match = match_section(MACTHER_API_URL, bearer_token, "Technical Skills", selected_job_details['technical_skill'], candidate['technical_skill'])
                                soft_skill_match = match_section(MACTHER_API_URL, bearer_token, "Soft Skills", selected_job_details['soft_skill'], candidate['soft_skill'])
                                certificate_match = match_section(MACTHER_API_URL, bearer_token, "Certificates", selected_job_details['certificate'], candidate['certificate'])

                                matching_data = [education_match["json"], experience_match["json"], responsibility_match["json"], technical_skill_match["json"], soft_skill_match["json"], certificate_match["json"]]
                                
                                all_scores = {
                                    "degree": education_match["json"]["score"],
                                    "experience": experience_match["json"]["score"],
                                    "technical_skill": technical_skill_match["json"]["score"],
                                    "responsibility": responsibility_match["json"]["score"],
                                    "certificate": certificate_match["json"]["score"],
                                    "soft_skill": soft_skill_match["json"]["score"],
                                }

                                overall_score = calculate_overall_score(all_scores)
                                insert_matching(overall_score, matching_data, candidate, selected_job_details['job_id'])

                                matching_results.append({
                                    "Candidate Name": candidate["candidate_name"],
                                    "Match Score": overall_score,
                                })

                            # Display the matching results
                            if matching_results:
                                st.write("### Matching Results")
                                st.table(matching_results)

                else:
                    st.write("No candidates found in the database.")

        except Exception as e:
            st.error(f"❌ Failed to fetch candidates or matchings from the database: {str(e)}")








if __name__ == "__main__":
    main()
