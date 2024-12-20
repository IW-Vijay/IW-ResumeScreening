import requests

def convert_pdf_to_binary(file_path):
    try:
        # Open the PDF file in binary read mode
        with open(file_path, 'rb') as file:
            binary_data = file.read()
        return binary_data
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
pdf_file_path = "uploads/candidates/VIjay_Verma.pdf"  # Replace with the path to your PDF file

# Prepare the file for uploading
try:
    with open(pdf_file_path, 'rb') as pdf_file:
        #files = {'file': (pdf_file_path, pdf_file, 'application/pdf')}
        files = convert_pdf_to_binary(pdf_file_path)
        #print(files)
        response = requests.post(
            "http://localhost:3000/api/v1/attachments/84f06a5d-b268-4ee8-adfc-c008273087e7/38f7d98d-8f06-4c2d-b121-d4dad3a38275",
            headers={"Authorization": "Bearer aW8IQI_KyF0m9JmoNeQww8Pmj_2bg5ydT-maQATinvg","Content-Type":"multipart/form-data"},
            files= files
        )

        print(f"Status Code: {response.status_code}")
        print("Response Content:", response.text)  # Raw response for debugging

        if response.headers.get("Content-Type") == "application/json":
            data = response.json()
            print("Parsed JSON Response:", data)
        else:
            print("The response is not in JSON format.")
except requests.exceptions.RequestException as e:
    print(f"An HTTP error occurred: {e}")
except Exception as e:
    print(f"An error occurred: {e}")