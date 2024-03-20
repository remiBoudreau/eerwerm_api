from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
import csv
import json
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow requests only from localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000", "http://127.0.0.1", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

POSTALCODE_MAPPING_PATH = 'postalCodeMapping.csv'
DATA_PATH = 'data.csv'

# API endpoint to serve data
@app.get("/data") 
async def load_json():
    """
    Serve client data
    """
    csvFilePath = DATA_PATH
    data_dict = await load_csv(csvFilePath)

    return json.dumps(data_dict, indent=4)
    
# API endpoint to serve data
@app.get("/csv") 
async def load_csv(csvFilePath: str):
    """
    Serve client data
    """
    data = {"data": []}
    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csv_reader = csv.reader(csvf, delimiter=',')
        
        # Get headers
        headers = next(csv_reader)
        
        # Iterate over each row after the header in the csv
        for row in csv_reader:
            data_entry = {}
            for headerIn, header in enumerate(headers):
                data_entry[header] = row[headerIn]
            data["data"].append(data_entry)
    return data

@app.get("/postalCodeMapper")
async def postalCodeMapper():
    """
    Map postal codes to neighborhoods
    """
    # Send 'postalCodeMapping' csv_file_path to api
    postalCodeMappingData = await load_csv(POSTALCODE_MAPPING_PATH)
    # Send 'all_data' csv_file_path to api
    data = await load_csv(DATA_PATH)
    # Check all rows in column 'neighborhood' in 'all_data' csv file for none 
    for row in data['data']:
        if not row['neighborhood']:
            # If empty, use 'postalCode' to get 'neighborhood' from 'postalCodeMapping' csv file
            for postalCodeMappingRow in postalCodeMappingData['data']:
                if postalCodeMappingRow['postalCode'] == row['postalCode']:
                    row['neighborhood'] = postalCodeMappingRow['neighborhood']
    # Resave all_data with 'neighborhood' column updated
    with open(data, 'w', newline='', encoding='utf-8') as csvf:
        csv_writer = csv.writer(csvf, delimiter=',')
        # Write headers
        csv_writer.writerow(data['data'][0].keys())
        # Write data
        for row in data['data']:
            csv_writer.writerow(row.values())
    return "Postal code mapping complete"
#
# API endpoint to retrieve comprehensive chemical data for multiple IDs
@app.get("/help")
async def help():
    return "Placeholder"