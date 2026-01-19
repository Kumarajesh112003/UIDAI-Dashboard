import os
import zipfile

def unzip_data(zip_name, extract_to):
    if os.path.exists(zip_name):
        with zipfile.ZipFile(zip_name, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

def prepare_directories():
    os.makedirs('./data_enrolment', exist_ok=True)
    os.makedirs('./data_demographic', exist_ok=True)
    os.makedirs('./data_biometric', exist_ok=True)

    unzip_data('api_data_aadhar_enrolment.zip', './data_enrolment')
    unzip_data('api_data_aadhar_demographic.zip', './data_demographic')
    unzip_data('api_data_aadhar_biometric.zip', './data_biometric')
