import time
import math
#import other files
from stream_queue.log_stream import LogStream
from database.vector_memory import vectorMemory
from database.sql_archive import sql_Memory

print("Async background work booting..")
#intializes over her
stream = LogStream()
vector_store = vectorMemory()
db = sql_Memory()

#makes the script to run on loop
#It constantly polls the stream queue in the background, processes the AI vector math, and writes to the SQL database entirely on its own time.

while True:
    try:
        queue_item = stream.redpop()

        # If the queue is currently empty, take a short breath and look again
        if not queue_item:
            time.sleep(0.5)
            continue
        print(f"📥 Processing log pulled from queue for IP: {queue_item['ip_address']}")
            
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
        
        print(f"✅ Successfully processed and archived log for {queue_item['ip_address']}")
        print(f"📈 Analytics -> Score: {threat_score}% | Status: {status}")
        print("-" * 40)
    
    except Exception as e:
        print(f"Worker process encountered error:{e}")
        time.sleep(1)


