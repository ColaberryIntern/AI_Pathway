#\!/bin/bash
# Communication Intelligence Pipeline - runs every 30 minutes
# Ingests new emails from Luda/Vivek and syncs to Basecamp

curl -s -X POST http://localhost:3000/api/communication/run?lookback_hours=1   -H "Content-Type: application/json"   >> /var/log/comm_pipeline.log 2>&1

echo " [$(date)]" >> /var/log/comm_pipeline.log
