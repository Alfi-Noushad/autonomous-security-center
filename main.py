import uvicorn
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
#import the other file
from stream_queue.log_stream import LogStream

#Tracks the ip address and their request tracking.
RATE_LIMIT_WINDOW_SECONDS = 10
MAX_REQUESTS_PER_WINDOW = 5
ip_request_history = {}


#creates the fastapi 
app = FastAPI(title="Autonomous Security Operations Center (ASOC)",
              description="")

#intializes over her
stream = LogStream()

#sets up the data validation pydantic
class requestAsessment(BaseModel):
    ip_address: str
    log_message: str

#it is used for the health check web api,(when the user enter the '/'[home page] it runs async..) 
@app.get("/")
async def health_check():
   return{"status":"Online"}
#_____________________________________________________

#sets up the route post(endpoint)
@app.post("/evaluate-risk")
async def evaluate_risk(data: requestAsessment, request: Request):

    #_____implements the rate limit feature over here
    #identify who is calling the api
    client_ip = request.client.host
    current_time = time.time()

    # [1] Rate Limiter Guard ____

    if client_ip not in ip_request_history:
        #enter the ip to the dic as the key
        ip_request_history[client_ip] = []
    
    #removes the timestamps(val in dict) that happend more than 10 sec
    ip_request_history[client_ip] = [
        timestamp for timestamp in ip_request_history[client_ip]
        if current_time - timestamp < RATE_LIMIT_WINDOW_SECONDS
    ]

    #If they have made 5 or more requests in the last 10 seconds, shut it down!
    if len(ip_request_history[client_ip]) >= MAX_REQUESTS_PER_WINDOW:
           raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded! Max {MAX_REQUESTS_PER_WINDOW} requests per {RATE_LIMIT_WINDOW_SECONDS} seconds allowed."
           )
    
    # Log this successful request timestamp
    ip_request_history[client_ip].append(current_time)        

    # [2] Queue Backpressure Guard _____

    # Read the file array length using your shared JSON file method
    current_queue = stream._read_queue()
    if len(current_queue) >= 50:
        raise HTTPException(
            status_code=503,
            detail="System high backpressure. Security queue buffer full, please retry shortly."
        )

    # Ingestion via buffer stream
    # ( Now runs only going through both the guard unlike before )
    stream.redpush(data.ip_address, data.log_message)
   
   # Return a 202 Accepted status instantly to the user
    return {
        "status": "Accepted",
        "message": "Security log stream successfully pushed into secure in-memory queue. Processing asynchronously.",
        "ingested_ip": data.ip_address
    }

if __name__ == "__main__":
    print()
    #runs on this
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



