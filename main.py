import math
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
#import the other file
from stream_queue.log_stream import LogStream
from database.vector_memory import vectorMemory
from database.sql_archive import sql_Memory

#creates the fastapi 
app = FastAPI(title="Autonomous Security Operations Center (ASOC)",
              description="")

#intializes over her
stream = LogStream()
vector_store = vectorMemory()
db = sql_Memory()


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
    queue_item = stream.redpop()
    
    if not queue_item:
        return {"error": "Queue ingestion failure"}
        
    # AI Vector similarity lookup
    ai_results = vector_store.analyze_similarity(queue_item["log_message"])
    distance_score = ai_results["vector_geometric_distance"]
    closest_profile = ai_results["closest_known_exploit_profile"]
    
    # Maps 0.0 distance -> 100% risk, decaying smoothly as distance grows
    decay_factor = -2.5
    calculated_index = 100.0 * math.exp(decay_factor * distance_score)
    threat_score = round(max(0.0, min(100.0, calculated_index)), 1)

    # Classification Buckets
    if distance_score <= 0.65:
        status = "CRITICAL_THREAT_DETECTED"
    elif 0.65 < distance_score <= 0.95:
        status = "SUSPICIOUS_ANOMALY"
    else:
        status = "SAFE_TRAFFIC"
        
    # Log permanently to SQLite database archive
    db.save_alert(
        ip=queue_item["ip_address"],
        log=queue_item["log_message"],
        score=threat_score,
        status=status
    )
    
    return {
        "analysis_status": status,
        "evaluated_threat_index": threat_score,
        "closest_known_exploit_profile": closest_profile,
        "vector_geometric_distance": distance_score
    }


if __name__ == "__main__":
    print()
    #runs on this
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)



