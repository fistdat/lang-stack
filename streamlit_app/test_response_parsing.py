#!/usr/bin/env python3
"""
Test response parsing for Langflow API
"""
import requests
import json

def extract_response_text(response):
    """Extract clean text from Langflow response"""
    response_text = "No response text found"
    try:
        # Try to extract meaningful response from the nested structure
        if isinstance(response, dict) and "outputs" in response:
            outputs = response["outputs"]
            if isinstance(outputs, list) and len(outputs) > 0:
                first_output = outputs[0]
                if "outputs" in first_output and isinstance(first_output["outputs"], list) and len(first_output["outputs"]) > 0:
                    nested_output = first_output["outputs"][0]
                    if "results" in nested_output and "message" in nested_output["results"]:
                        message = nested_output["results"]["message"]
                        if "text" in message:
                            response_text = message["text"]
                        elif "data" in message and "text" in message["data"]:
                            response_text = message["data"]["text"]
        
        # Fallback: try other common paths
        if response_text == "No response text found":
            if "result" in response:
                response_text = str(response["result"])
            elif "message" in response:
                response_text = str(response["message"])
            else:
                response_text = json.dumps(response, indent=2)
                
    except Exception as e:
        response_text = f"Error parsing response: {str(e)}"
    
    return response_text

def test_langflow_response():
    """Test the actual API and response parsing"""
    print("🔍 Testing Langflow API response parsing...")
    
    url = "http://localhost:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761"
    
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": "Test response parsing - cho tôi 3 tòa nhà bất kỳ"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print("✅ API call successful!")
        
        # Test our parsing function
        extracted_text = extract_response_text(result)
        
        print("\n📄 Extracted clean text:")
        print("=" * 50)
        print(extracted_text)
        print("=" * 50)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_langflow_response()