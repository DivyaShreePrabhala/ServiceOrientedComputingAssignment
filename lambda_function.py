import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table_name = 'HealthRecords'  
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    route_key = event['routeKey']
    
    if route_key == 'GET /health-records':
        return handle_get(event)
    elif route_key == 'GET /health-records/{recordId}':
        return handle_getItemId(event)
    elif route_key == 'POST /health-records':
        return handle_post(event)
    elif route_key.startswith('PUT /health-records'):
        return handle_put(event)
    elif route_key.startswith('DELETE /health-records'):
        return handle_delete(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid route key'})
        }
    

def handle_get(event):
    path_parameters = event.get('pathParameters', {})
    record_id = path_parameters.get('recordId')
    if record_id:
        return get_health_record(record_id)
    else:
        return get_all_health_records()
        
def handle_getItemId(event):
    path_parameters = event.get('pathParameters', {})
    record_id = path_parameters.get('recordId')
    if record_id:
        return get_health_record(record_id)
    else:
        return get_all_health_records()

def handle_post(event):
    try:
        health_record = json.loads(event['body'])
        response = table.put_item(Item=health_record)
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Health record created successfully'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handle_put(event):
    record_id = event.get('pathParameters', {}).get('recordId')
    
    if record_id:
        try:
            health_record = json.loads(event['body'])
            response = table.update_item(
                Key={'recordId': record_id},
                UpdateExpression='SET #attr1 = :val1, #attr2 = :val2',
                ExpressionAttributeNames={'#attr1': 'attribute1', '#attr2': 'attribute2'},
                ExpressionAttributeValues={':val1': health_record['attribute1'], ':val2': health_record['attribute2']},
                ReturnValues='UPDATED_NEW'
            )
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Health record updated successfully'})
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Record ID is required for update'})
        }

def handle_delete(event):
    record_id = event.get('pathParameters', {}).get('recordId')
    
    if record_id:
        return delete_health_record(record_id)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Record ID is required for deletion'})
        }

def get_health_record(record_id):
    try:
        response = table.get_item(Key={'recordId': record_id})
        health_record = response.get('Item')
        if health_record:
            return {
                'statusCode': 200,
                'body': json.dumps(health_record)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Health record not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_all_health_records():
    try:
        response = table.scan()
        health_records = response.get('Items', [])
        return {
            'statusCode': 200,
            'body': json.dumps({'healthRecords': health_records})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def delete_health_record(record_id):
    try:
        response = table.delete_item(Key={'recordId': record_id})
        return {
            'statusCode': 204,
            'body': json.dumps({})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
