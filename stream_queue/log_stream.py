# stream_queue/log_stream.py
import json
import os

class LogStream:
    def __init__(self):
        # We point to a shared physical file in your root directory
        self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "shared_queue.json"))
        # Clean flush on fresh application cluster startup if needed
        if not os.path.exists(self.file_path):
            self._write_queue([])

    def _read_queue(self):
        try:
            if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _write_queue(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def redpush(self, ip_address: str, log_message: str):
        payload = {"ip_address": ip_address, "log_message": log_message}
        
        # Read current state, append payload, and save back to shared storage
        queue = self._read_queue()
        queue.append(payload)
        self._write_queue(queue)
        
        print(f"📦 Shared Queue Received & Buffered: {log_message}")

    def redpop(self):
        queue = self._read_queue()
        if not queue:
            return None
            
        # Pop the oldest item (First In, First Out queue structure)
        processed_dictionary = queue.pop(0)
        self._write_queue(queue)
        return processed_dictionary