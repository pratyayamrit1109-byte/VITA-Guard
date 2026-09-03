from fastapi import FastAPI, WebSocket
import numpy as np
import json
import uvicorn

app = FastAPI(title="VITA-Guard Backend")

# Thresholds based on Dual Kinetic Profile
THRESHOLDS = {
    "industrial": {"impact": 25.0, "flatline_variance": 0.5},
    "elderly": {"impact": 15.0, "flatline_variance": 0.2}
}

@app.websocket("/ws/sensor")
async def sensor_endpoint(websocket: WebSocket):
    await websocket.accept()
    current_mode = "industrial" # Default profile
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Extract 3-axis acceleration
            ax, ay, az = payload.get("x", 0), payload.get("y", 0), payload.get("z", 0)
            
            # Vector Magnitude Model
            magnitude = np.sqrt(ax**2 + ay**2 + az**2)
            
            # Phase 1: Impact Check
            if magnitude > THRESHOLDS[current_mode]["impact"]:
                await websocket.send_json({"alert": "impact_detected", "magnitude": magnitude})
                
            # (In a full deployment, Phase 2 Post-shock micro-motion flatline logic goes here)
            
    except Exception as e:
        print(f"Connection closed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)