#!/bin/bash

# Test Langflow API connection
echo "Testing Langflow API connection..."

# Get API key from environment variable
if [ -z "$LANGFLOW_API_KEY" ]; then
    echo "Error: LANGFLOW_API_KEY environment variable not found. Please set your API key in the environment variables."
    exit 1
fi

echo "API Key found: ${LANGFLOW_API_KEY:0:10}..."
echo "Testing connection to Langflow API..."

curl --request POST \
     --url 'http://localhost:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761?stream=false' \
     --header 'Content-Type: application/json' \
     --header "x-api-key: $LANGFLOW_API_KEY" \
     --data '{
                   "output_type": "chat",
                   "input_type": "chat",
                   "input_value": "hello world!"
                 }' \
     --silent \
     --show-error \
     --fail \
     --write-out "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n"

if [ $? -eq 0 ]; then
    echo "✅ Connection successful!"
else
    echo "❌ Connection failed!"
fi