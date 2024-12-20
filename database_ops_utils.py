import os
import psycopg2
from psycopg2.extras import execute_values

from dotenv import load_dotenv

load_dotenv()
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB_NAME"),
    "user": "postgres",
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": "localhost",
    "port": 5432
}

# Function to insert job description analysis into the database
def insert_job_description(data):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Insert query
        query = """
        INSERT INTO job_descriptions (
            degree, 
            experience, 
            technical_skill, 
            responsibility, 
            certificate, 
            soft_skill, 
            yoe, 
            name
        ) 
        VALUES (
            %(degree)s,
            %(experience)s,
            %(technical_skill)s,
            %(responsibility)s,
            %(certificate)s,
            %(soft_skill)s,
            %(yoe)s,
            %(name)s
        );
        """

        # Execute the query
        cursor.execute(query, data)
        connection.commit()
        print("Job description data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()



# Function to insert job description analysis into the database
def insert_candidate_details(data):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Insert query
        query = """
        INSERT INTO candidates (
            candidate_name,
            phone_number,
            email,
            degree,
            experience,
            technical_skill,
            responsibility,
            certificate,
            soft_skill,
            yoe,
            portfolios
        ) VALUES (
            %(candidate_name)s,
            %(phone_number)s,
            %(email)s,
            %(degree)s,
            %(experience)s,
            %(technical_skill)s,
            %(responsibility)s,
            %(certificate)s,
            %(soft_skill)s,
            %(yoe)s,
            %(portfolio)s
        )
        """

        # Execute the query
        cursor.execute(query, data)
        connection.commit()
        print("Candidate data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()




def fetch_all_job_descriptions():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Fetch all job descriptions
        query = """
        SELECT * FROM job_descriptions
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]

        # Convert rows to a list of dictionaries
        result = [dict(zip(column_names, row)) for row in rows]

        return result

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()




def fetch_all_candidates():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Fetch all job descriptions
        query = """
        SELECT * FROM candidates
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]

        # Convert rows to a list of dictionaries
        result = [dict(zip(column_names, row)) for row in rows]

        return result

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()


def fetch_matchings(selected_job_id):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Fetch all job descriptions securely using parameterized queries
        query = """
        SELECT * FROM matchings WHERE job_id = %s
        """
        cursor.execute(query, (selected_job_id,))
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [desc[0] for desc in cursor.description]

        # Convert rows to a list of dictionaries
        result = [dict(zip(column_names, row)) for row in rows]

        return result

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    finally:
        # Ensure proper cleanup
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


import psycopg2

import psycopg2

def insert_matching(matching_score, data, candidate, job_id):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Extract the relevant data from the list
        education_score = data[0]['score']
        education_comment = data[0]['justification']
        
        experience_score = data[1]['score']
        experience_comment = data[1]['justification']
        
        responsibilitie_score = data[2]['score']
        responsibilitie_comment = data[2]['justification']
        
        technicall_skills_score = data[3]['score']
        technicall_skills_comment = data[3]['justification']
        
        soft_skills_score = data[4]['score']
        soft_skills_comment = data[4]['justification']
        
        certificates_score = data[5]['score']
        certificates_comment = data[5]['justification']

        # Calculate the overall matching score
        matching_score = (education_score + experience_score + responsibilitie_score +
                          technicall_skills_score + soft_skills_score + certificates_score) / 6

        # Insert or update query
        query = """
        INSERT INTO matchings (
            candidate_id, candidate_name, candidate_phone_number, job_id, matching_score,
            education_comment, education_score,
            experience_comment, experience_score,
            responsibilitie_comment, responsibilitie_score,
            technicall_skills_comment, technicall_skills_score,
            soft_skills_comment, soft_skills_score,
            certificates_comment, certificates_score
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s
        )
        ON CONFLICT (candidate_id, job_id) 
        DO UPDATE SET
            matching_score = EXCLUDED.matching_score,
            education_comment = EXCLUDED.education_comment,
            education_score = EXCLUDED.education_score,
            experience_comment = EXCLUDED.experience_comment,
            experience_score = EXCLUDED.experience_score,
            responsibilitie_comment = EXCLUDED.responsibilitie_comment,
            responsibilitie_score = EXCLUDED.responsibilitie_score,
            technicall_skills_comment = EXCLUDED.technicall_skills_comment,
            technicall_skills_score = EXCLUDED.technicall_skills_score,
            soft_skills_comment = EXCLUDED.soft_skills_comment,
            soft_skills_score = EXCLUDED.soft_skills_score,
            certificates_comment = EXCLUDED.certificates_comment,
            certificates_score = EXCLUDED.certificates_score;
        """

        # Execute the query with values
        cursor.execute(query, (
            candidate["candidate_id"], candidate["candidate_name"], candidate["phone_number"], job_id, matching_score,
            education_comment, education_score,
            experience_comment, experience_score,
            responsibilitie_comment, responsibilitie_score,
            technicall_skills_comment, technicall_skills_score,
            soft_skills_comment, soft_skills_score,
            certificates_comment, certificates_score
        ))

        # Commit the transaction
        connection.commit()
        print("Candidate data inserted/updated successfully.")

    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()



def calculate_overall_score(data):
    weights = {
        "degree": 0.1,  # The importance of the candidate's degree
        "experience": 0.2,  # The weight given to the candidate's relevant work experience
        "technical_skill": 0.3,  # Weight for technical skills and qualifications
        "responsibility": 0.25,  # How well the candidate's past responsibilities align with the job
        "certificate": 0.1,  # The significance of relevant certifications
        "soft_skill": 0.05,  # Importance of soft skills like communication, teamwork, etc.
    }

    # Calculate the overall score
    overall_score = sum(data[key] * weights[key] for key in weights)
    
    return (overall_score*10)