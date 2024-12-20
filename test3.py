def calculate_overall_score(data):
    weights = {
        "degree": 0.1,  # The importance of the candidate's degree
        "experience": 0.2,  # The weight given to the candidate's relevant work experience
        "technical_skill": 0.3,  # Weight for technical skills and qualifications
        "responsibility": 0.25,  # How well the candidate's past responsibilities align with the job
        "certificate": 0.1,  # The significance of relevant certifications
        "soft_skill": 0.05,  # Importance of soft skills like communication, teamwork, etc.
    }

    # Ensure all necessary keys are present in data
    if not all(key in data for key in weights):
        raise ValueError("Input data is missing one or more required keys.")

    # Calculate the overall score
    overall_score = sum(data[key] * weights[key] for key in weights)
    
    return overall_score*10

# Example usage
candidate_data = {
    "degree": 8,  # Example score out of 10
    "experience": 7,
    "technical_skill": 9,
    "responsibility": 8,
    "certificate": 6,
    "soft_skill": 7
}

score = calculate_overall_score(candidate_data)
print(f"Overall Score: {score}")
