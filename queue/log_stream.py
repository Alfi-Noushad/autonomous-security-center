import fakeredis
import json


class LogStream:
    def __init__(self):
        # decode_responses=True forces Redis to return data as strings instead of raw binary bytes
        self.redis = fakeredis.FakeStrictRedis(decode_responses=True)

    def redpush(self, ip_address: str, log_message: str):
        #convert the ouptut to python dictionary
        payload = {"ip_address": ip_address,"Log_messsage": log_message}
        # Convert that dictionary into a plain text string 
        serialized_data = json.dumps(payload)

        #Push it into a list key named "security_queue" inside Redis memory
        self.redis.rpush("security_queue", serialized_data)
        print(f"Redis Queue Received: {log_message}")

    def redpop(self):
        #pop the value from the list (security_queue)
        raw_data = self.redis.lpop("security_queue")

        #if queue is empty
        if not raw_data:
            return None
        
        #now we convert the plain text to working python diction..
        processed_dictionary = json.loads(raw_data)
        return processed_dictionary