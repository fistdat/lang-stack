import streamlit as st
import requests
import os
import json
from typing import Optional, Dict, Any

st.set_page_config(
    page_title="Energy AI Optimizer: A Multi-Agent System for Building Energy Consumption Analysis and Optimization",
    page_icon="🎓",
    layout="centered"
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
    # Academic thesis header
    st.markdown("""
    # Energy AI Optimizer: A Multi-Agent System for Building Energy Consumption Analysis and Optimization
    
    **MINISTRY OF EDUCATION AND TRAINING**  
    **FPT UNIVERSITY**
    
    ---
    
    **A thesis submitted in conformity with the requirements for the degree of Master of Software Engineering**
    
    **By:** Hoang Tuan Dat  
    **Supervisor:** Assoc. Prof. Phan Duy Hung  
    **© Copyright by Hoang Tuan Dat 2025**
    """)
    st.markdown("---")
    
    # Get API configuration from environment (hidden from UI)
    api_key = os.environ.get("LANGFLOW_API_KEY", "")
    api_url = os.environ.get("LANGFLOW_API_URL", "http://host.docker.internal:7860/api/v1/run/3f229440-4079-4ee6-bcd3-341accdd9761")
    
    # Main content area - expanded chat interface
    st.header("💬 Energy AI Chat Interface")
    
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
            error_msg = "Please configure the API URL in the environment variables."
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_msg
            })

if __name__ == "__main__":
    main()