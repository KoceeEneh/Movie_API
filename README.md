# Movie API Project

# Overview
The Movie API Project is a cloud-based serverless application that fetches movie details from the OMDb API, stores them in an AWS DynamoDB table, and saves movie posters in an S3 bucket. the API is powered by AWS lambda functions that provide movie-related data via HTTP requests.

# Features
- Fetch movie details using the OMDb API.

- Upload movie posters to an AWS S3 bucket.

- Store movie metadata in AWS DynamoDB.

- Serverless API using AWS Lambda functions.

- Retrieve all movies stored in the database.

- Query movies by release year.
---

# Tech Stack
- Python (Boto3, Requests, JSON, dotenv)

- AWS Services:

- AWS Lambda

- AWS S3

- AWS DynamoDB

- AWS Secrets Manager

- OMDb API (for fetching movie data)
---

# Prerequisites
- AWS Account with IAM permissions for S3, DynamoDB, Lambda, and Secrets Manager.

- Python 3.13 installed.

- AWS CLI installed and configured.

- OMDb API Key stored in AWS Secrets Manager.
---

# Installation

**1. Install Dependencies**

```bash
pip install -r requirements.txt
```

**2. Configure AWS Credentials**
Ensure you have valid AWS credentials configured using:

```bash
aws configure
```

**3. Create AWS Resources**
Run the Python script to create the required AWS resources

```bash
python boto3_m.py
```
this should:
- Create an S3 bucket.

- Create a DynamoDB table.

- Retrieve the OMDb API key from AWS Secrets Manager.

- Fetch and store movie data.
---

## AWS Lambda Functions
**1. Get All Movies**

- Retrieves all movies stored in DynamoDB.

- Trigger: HTTP Request via Function URL or API Gateway.

https://github.com/KoceeEneh/Movie_API/blob/783403cf0148346d20017833590a5aa87ccabb1b/boto3_m.py#L136

**2. Get Movie by Year**

- Fetches movies released in a specific year.

- Trigger: HTTP Request with query parameter (year).
# perlink

## Deploying AWS Lambda Functions
1. Package the function

```bash
zip -r lambda_function.zip boto3_m.py
```

2. Deploy to AWS

```bash
aws lambda create-function \
    --function-name GetMovies \
    --runtime python3.x \
    --role <EXECUTION_ROLE_ARN> \
    --handler boto3_m.lambda_get_movies \
    --zip-file fileb://lambda_function.zip
```
3. Enable Function URL (Public Access)

```bash
aws lambda create-function-url-config \
  --function-name GetMovies \
  --auth-type NONE
```

## Testing the API
1. invoke the Lambda function

```bash
aws lambda invoke --function-name GetMovies response.json
```

3. call the function URL

```bash
curl https://your-function-url.aws-region.on.aws/
```

4. can use postman to test too

**function output**

<img width="1283" alt="Screenshot 2025-03-14 at 02 02 58" src="https://github.com/user-attachments/assets/a13c57ae-a816-4d5f-bedf-f01d82e2c183" />

**poster url output**

<img width="1326" alt="Screenshot 2025-03-14 at 02 03 19" src="https://github.com/user-attachments/assets/503dd10c-b884-4809-b68f-c526b74ebed0" />



