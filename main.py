import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
#import the other file
from stream_queue.log_stream import LogStream
from database.vector_memory import VectorMemory
from database.sql_archive import SqlMemory

#creates the fastapi 
app = FastAPI(title="Autonomous Security Operations Center (ASOC)",
              description="")

#intializes over her
stream = LogStream()
vector_store = VectorMemory()
db = SqlMemory()


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
async def calculate_risk(data: requestAsessment):

    #|||step-1: buffer ingestion
    stream.redpush(data.ip_address,data.log_message)

    #Pop it right back out of the list queue to process it
    queue_item = stream.redpop()
    if not queue_item:
        return {"status": "Queue processing failed"}
    
    #|||step-2: vector search matching
    ai_results = vector_store.analyze_similarity(queue_item["log_message"])

    #takes the closest result and score of it
    closest_match_text = ai_results['documents'][0][0]
    distance_score = ai_results['distances'][0][0]

    #|||step-3: decision making
    #intialized
    threat_score = 10.0
    status = "SAFE_TRAFFIC"

    if distance_score < 1.1:
        threat_score = 94.7
        status = "CRITICAL_THREAT_DETECTED"

    #|||step-4: DB storing 
    db.save_alert(queue_item["ip_address"], queue_item["log_message"], threat_score, status)


    return {
        "analysis_status": status,
        "evaluated_threat_index": threat_score,
        "closest_known_exploit_profile": closest_match_text,
        "vector_geometric_distance": round(distance_score, 4)
        }


if __name__ == "__main__":
    print()
    #runs on this
    uvicorn.run(app,host="127.0.0.1", port=8000, reload=True)



