#!/usr/bin/env python3
"""
Test script for Langflow integration
"""
import requests
import json
import sys

def test_langflow_connection():
    """Test connection to Langflow API"""
    print("🔍 Testing Langflow API connection...")
    
    url = "http://localhost:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761"
    
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": "Xin chào! Đây là test kết nối từ Streamlit app."
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Connection successful!")
        print(f"📊 Response status: {response.status_code}")
        print(f"📝 Session ID: {result.get('session_id', 'N/A')}")
        
        # Extract the message text
        if 'outputs' in result and result['outputs']:
            outputs = result['outputs'][0]
            if 'outputs' in outputs and outputs['outputs']:
                message_data = outputs['outputs'][0]['results']['message']
                message_text = message_data.get('text', 'No message text found')
                print(f"💬 AI Response: {message_text}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_streamlit_health():
    """Test Streamlit app health"""
    print("\n🔍 Testing Streamlit app health...")
    
    try:
        response = requests.get("http://localhost:8501/_stcore/health", timeout=10)
        response.raise_for_status()
        print("✅ Streamlit app is healthy!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Streamlit health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting integration tests...\n")
    
    # Test Streamlit health
    streamlit_ok = test_streamlit_health()
    
    # Test Langflow connection
    langflow_ok = test_langflow_connection()
    
    print(f"\n📋 Test Results:")
    print(f"   Streamlit App: {'✅ OK' if streamlit_ok else '❌ FAIL'}")
    print(f"   Langflow API:  {'✅ OK' if langflow_ok else '❌ FAIL'}")
    
    if streamlit_ok and langflow_ok:
        print("\n🎉 All tests passed! Integration is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        sys.exit(1)