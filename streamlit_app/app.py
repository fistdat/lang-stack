import streamlit as st
import requests
import os
import json
from typing import Optional, Dict, Any

st.set_page_config(
    page_title="Langflow Integration App",
    page_icon="🚀",
    layout="wide"
)

def langflow_api_call(input_value: str, api_key: str, url: str) -> Optional[Dict[Any, Any]]:
    """
    Make API call to Langflow
    """
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": input_value
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Only add API key if provided
    if api_key and api_key.strip() and api_key != "your_api_key_here":
        headers["x-api-key"] = api_key
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"JSON parsing error: {e}")
        return None

def main():
    st.title("🚀 Langflow Integration App")
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Langflow API Key",
            type="password",
            value=os.environ.get("LANGFLOW_API_KEY", ""),
            help="Enter your Langflow API key"
        )
        
        # API URL input
        api_url = st.text_input(
            "Langflow API URL",
            value=os.environ.get("LANGFLOW_API_URL", "http://localhost:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761"),
            help="Enter the complete Langflow API endpoint URL"
        )
        
        # Test connection button
        if st.button("🔍 Test Connection"):
            if api_url:
                test_response = langflow_api_call("test connection", api_key, api_url)
                if test_response:
                    st.success("✅ Connection successful!")
                    st.json(test_response)
                else:
                    st.error("❌ Connection failed!")
            else:
                st.warning("⚠️ Please provide the API URL")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("What would you like to ask?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from Langflow
            if api_url:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = langflow_api_call(prompt, api_key, api_url)
                        
                        if response:
                            # Extract the actual response text from Langflow
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
                            
                            st.markdown(response_text)
                            
                            # Add assistant response to chat history
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": response_text
                            })
                        else:
                            error_msg = "Sorry, I couldn't process your request. Please check the API configuration."
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": error_msg
                            })
            else:
                error_msg = "Please configure the API URL in the sidebar."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_msg
                })
    
    with col2:
        st.header("📊 Status")
        
        # Connection status
        if api_url:
            st.success("🔗 API URL Configured")
            if api_key and api_key.strip() and api_key != "your_api_key_here":
                st.info("🔐 API Key Set")
            else:
                st.info("🔓 API Key Optional")
        else:
            st.warning("⚠️ API URL Not Configured")
        
        # Chat statistics
        st.metric("Messages", len(st.session_state.messages))
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # API response format toggle
        show_raw_response = st.checkbox("Show Raw API Response")
        
        if show_raw_response and st.session_state.messages:
            st.subheader("🔍 Raw Response")
            if st.session_state.messages:
                last_response = st.session_state.messages[-1]
                if last_response["role"] == "assistant":
                    st.code(last_response["content"], language="json")

if __name__ == "__main__":
    main()