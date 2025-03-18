import json
import boto3
import os
from decimal import Decimal
import logging

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get DynamoDB table name
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'visitor-counter')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# CORS headers for API response
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',  # In production, should be restricted to your website domain
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
}

def lambda_handler(event, context):
    """
    Lambda handler function for processing API Gateway requests
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Handle OPTIONS request (preflight request)
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({})
        }
    
    try:
        # Try to increment counter and get new value
        new_count = increment_counter()
        
        # Prepare API response
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'count': new_count
            })
        }
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': str(e)
            })
        }

def increment_counter():
    """
    Increment visitor counter and return new count
    
    Returns:
        int: Updated visitor count
    """
    # Use update_item to atomically update the counter
    try:
        response = table.update_item(
            Key={
                'counter_id': 'visitors'
            },
            UpdateExpression='ADD visitor_count :inc',
            ExpressionAttributeValues={
                ':inc': 1
            },
            ReturnValues='UPDATED_NEW'
        )
        
        # Get new count value from response
        updated_count = response.get('Attributes', {}).get('visitor_count', 0)
        
        # DynamoDB returns Decimal, convert to int
        if isinstance(updated_count, Decimal):
            updated_count = int(updated_count)
            
        logger.info(f"Successfully incremented counter to {updated_count}")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error incrementing counter: {str(e)}")
        
        # If record doesn't exist, create it
        if 'ValidationException' in str(e) or 'ResourceNotFoundException' in str(e):
            try:
                response = table.put_item(
                    Item={
                        'counter_id': 'visitors',
                        'visitor_count': 1
                    }
                )
                logger.info("Created new counter record with count 1")
                return 1
            except Exception as put_error:
                logger.error(f"Error creating counter: {str(put_error)}")
                raise put_error
        else:
            raise e 