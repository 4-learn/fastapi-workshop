curl -X POST http://127.0.0.1:8888/camera-events/search \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "cam-01",
    "event_type": "person"
  }'
