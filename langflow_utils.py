import requests
import json

def attach_files(chatflow_id, chat_id, files, token):
    """
    Upload files to the given chatflow and chat IDs.

    Parameters:
    - chatflow_id (str): The Chatflow ID
    - chat_id (str): The Chat ID
    - files (list): List of file paths to upload
    - token (str): Bearer token for authorization

    Returns:
    - Response JSON if successful
    - Error message otherwise
    """

    
    url = f"http://localhost:3000/api/v1/attachments/{chatflow_id}/{chat_id}"  # Replace with actual base URL

    try:
        # Prepare files for multipart/form-data
        files_payload = [
            ('files', (file_path, open(file_path, 'rb'), 'application/octet-stream'))
            for file_path in files
        ]

        # API request
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            files=files_payload
        )

        if response.status_code == 200:
            return response.json() # Successful response
        else:
            print(f"Upload failed. Status code: {response.status_code}")
            print("Response text:", response.text)
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def match_section(api_url, bearer_token, section_name ,jd_part, candidate_part):
    # Define the request payload
    payload = {
        "question": f'''Evaluate the following "{section_name}" section from a candidate's resume against the "{section_name}" requirement in the job description. If job description requirement is empty, then simply score 10 irrespective of candidate section.

        **Job Description:**
        -{section_name}: {jd_part}

        **Candidate Resume:**
        -{section_name}: {candidate_part}

        Provide the score and justification according to the scoring guidelines.
        '''
    }

    # Define the request headers
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Make the POST request
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    


def generate_question(api_url, bearer_token, data_for_questions):
    # Define the request payload
    payload = {
        "question": f'''Create question for candidate using below information:

            "Experience": {data_for_questions[0]}

            "Technical Skills": {data_for_questions[1]}

            "Previous Responsibilities": {data_for_questions[2]}

            "Certifications": {data_for_questions[3]}
        '''
    }

    # Define the request headers
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Make the POST request
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def parse_questions(data):
    parsed_data = {}
    for key, value in data.items():
        parsed_data[key] = value.split("&&&&")
    return parsed_data

