import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

#creates the fastapi 
app = FastAPI(title="Autonomous Security Operations Center (ASOC)",
              description="")

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
    return {"message": "Endpoint verified successfully"}


if __name__ == "__main__":
    print()
    #runs on this
    uvicorn.run(app,host="127.0.0.1", port=8000, reload=True)



