import boto3
import requests
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize AWS clients
s3 = boto3.client("s3")
secrets_manager = boto3.client("secretsmanager")
dynamodb = boto3.client("dynamodb")

# Constants
MOVIE_BUCKET = "movie-api.bucket-1"
TABLE_NAME = "movie2-api-table-1"
SECRET_NAME = "OMDbAPIKey"


# Create S3 bucket
def create_s3_bucket():

    try:

        s3.create_bucket(Bucket=MOVIE_BUCKET)
        print(f"S3 bucket '{MOVIE_BUCKET}' created successfully.")
    except Exception as e:

        print(f"Error creating S3 bucket: {e}")


# Create DynamoDB table
def create_dynamo_table():

    try:
        # Check if table exists
        existing_tables = dynamodb.list_tables()["TableNames"]
        if TABLE_NAME in existing_tables:
            print(f"Table '{TABLE_NAME}' already exists.")
            return

        # Create table if it doesn't exist
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[{"AttributeName": "movie_id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "movie_id", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        print(f"Created DynamoDB table: {TABLE_NAME}")
    except Exception as e:
        print(f"Error creating DynamoDB table: {e}")


# Get API key from AWS Secrets Manager
def get_secret():

    try:

        response = secrets_manager.get_secret_value(SecretId=SECRET_NAME)
        return json.loads(response["SecretString"]).get("OMDbAPIKey")
    except Exception as e:
        print(f"Error retrieving secret: {e}")

        return None


# Fetch movie data from OMDB API
def fetch_movie_data(movie_id):

    api_key = get_secret()

    if not api_key:
        raise ValueError("OMDb API Key not found!")

    url = f"http://www.omdbapi.com/?i={movie_id}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data.get("Response") == "True":
        return {
            "Title": data["Title"],
            "Year": data["Year"],
            "Released": data["Released"],
            "Genre": data["Genre"],
            "Language": data["Language"],
            "Poster": data["Poster"],
            "Plot": data.get("Plot", "N/A"),
            "imdbRating": data.get("imdbRating", "N/A"),
        }

    print("Movie not found!")
    return None


# Upload movie poster to S3
def upload_poster_to_s3(movie_data):

    try:
        poster_url = movie_data["Poster"]
        response = requests.get(poster_url, stream=True)

        if response.status_code == 200:
            file_name = f"{movie_data['Title']}.jpg"
            s3.put_object(
                Bucket=MOVIE_BUCKET,
                Key=file_name,
                Body=response.content,
                ContentType="image/jpeg",
            )
            return f"https://{MOVIE_BUCKET}.s3.amazonaws.com/{file_name}"
        print("Failed to download poster.")
    except Exception as e:
        print(f"Error uploading to S3: {e}")
    return None


# Store movie data in DynamoDB
def store_movie_data(movie_data, s3_url):

    try:

        item = {
            "movie_id": {"S": movie_data["Title"]},
            "info": {
                "M": {
                    "plot": {"S": movie_data.get("Plot", "N/A")},
                    "rating": {"S": movie_data.get("imdbRating", "N/A")},
                    "poster": {"S": s3_url},
                }
            },
        }
        dynamodb.put_item(TableName=TABLE_NAME, Item=item)
        print("Movie data stored in DynamoDB.")
    except Exception as e:
        print(f"Error storing movie data: {e}")


# Get all movies from DynamoDB
def lambda_get_movies(event, context):

    try:

        response = dynamodb.scan(TableName=TABLE_NAME)
        return {"statusCode": 200, "body": json.dumps(response.get("Items", []))}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error retrieving movies: {e}"}


# Get movies by year
def lambda_get_movies_by_year(event, context):

    try:

        year = event.get("queryStringParameters", {}).get("year")
        if not year:
            return {"statusCode": 400, "body": "Year parameter is required"}

        response = dynamodb.scan(TableName=TABLE_NAME)
        movies = [
            m
            for m in response.get("Items", [])
            if m.get("info", {}).get("M", {}).get("year", {}).get("S") == year
        ]

        return {"statusCode": 200, "body": json.dumps(movies)}
    except Exception as e:
        return {"statusCode": 500, "body": f"Error retrieving movies by year: {e}"}
