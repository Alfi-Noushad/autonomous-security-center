import math
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
#import the other file
from stream_queue.log_stream import LogStream


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

#sets up the route post(endpoint)
@app.post("/evaluate-risk")
async def evaluate_risk(data: requestAsessment):
    # Ingestion via buffer stream
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



