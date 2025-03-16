import json
import boto3
import os
from decimal import Decimal
import logging

# 設置日誌記錄器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 獲取 DynamoDB 表名
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'visitor-counter')

# 初始化 DynamoDB 客戶端
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# 用於 API 響應的 CORS 頭
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',  # 在生產環境中，應限制為您的網站域名
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
}

def lambda_handler(event, context):
    """
    Lambda 處理函數，用於處理 API Gateway 請求
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # 處理 OPTIONS 請求（預檢請求）
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({})
        }
    
    try:
        # 嘗試增加計數器並獲取新的值
        new_count = increment_counter()
        
        # 準備返回 API 響應
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
    增加訪問者計數器並返回新的計數
    
    Returns:
        int: 更新後的訪問者計數
    """
    # 使用 update_item 原子性地更新計數器
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
        
        # 從響應中獲取新的計數值
        updated_count = response.get('Attributes', {}).get('visitor_count', 0)
        
        # DynamoDB 返回的是 Decimal，轉換為 int
        if isinstance(updated_count, Decimal):
            updated_count = int(updated_count)
            
        logger.info(f"Successfully incremented counter to {updated_count}")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error incrementing counter: {str(e)}")
        
        # 如果記錄不存在，則創建它
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