import ssl
import base64
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

def main(params):
    validationResult = validateParams(params)
    if validationResult[0] != True:
        return {'error': validationResult[1]}
    else:
        validatedParams = validationResult[1]

    brokers = params['brokers']

    try:
        producer = KafkaProducer(
            api_version_auto_timeout_ms=15000,
            bootstrap_servers=brokers)

        print("Created producer")

        # only use the key parameter if it is present
        if 'key' in validatedParams:
            messageKey = validatedParams['key']
            producer.send(validatedParams['topic'], bytes(validatedParams['value'], 'utf-8'), key=bytes(messageKey, 'utf-8'))
        else:
            producer.send(validatedParams['topic'], bytes(validatedParams['value'], 'utf-8'))

        producer.flush()

        print("Sent message")
    except NoBrokersAvailable:
        # this exception's message is a little too generic
        return {'error': 'No brokers available. Check that your supplied brokers are correct and available.'}
    except Exception as e:
        return {'error': '{}'.format(e)}

    return {"success": True}

def validateParams(params):
    validatedParams = params.copy()
    requiredParams = ['brokers', 'topic', 'value']
    missingParams = []

    for requiredParam in requiredParams:
        if requiredParam not in params:
            missingParams.append(requiredParam)

    if len(missingParams) > 0:
        return (False, "You must supply all of the following parameters: {}".format(', '.join(missingParams)))

    if 'base64DecodeValue' in params and params['base64DecodeValue'] == True:
        try:
            validatedParams['value'] = base64.b64decode(params['value']).decode('utf-8')
        except:
            return (False, "value parameter is not Base64 encoded")

        if len(validatedParams['value']) == 0:
            return (False, "value parameter is not Base64 encoded")

    if 'base64DecodeKey' in params and params['base64DecodeKey'] == True:
        try:
            validatedParams['key'] = base64.b64decode(params['key']).decode('utf-8')
        except:
            return (False, "key parameter is not Base64 encoded")

        if len(validatedParams['key']) == 0:
            return (False, "key parameter is not Base64 encoded")

    return (True, validatedParams)
