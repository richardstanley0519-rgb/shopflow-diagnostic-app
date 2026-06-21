import streamlit as st
import google.generativeai as genai
import requests
import os

st.set_page_config(page_title="Shopflow Diagnostic Tool", layout="wide")
st.title("🏬 Shopflow Diagnostic App")
st.markdown("Analyze and optimize your retail or manufacturing workflows using AI.")

with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)

st.header("Diagnostic Input")
workflow_data = st.text_area("Paste your shopflow data or describe the workflow process:", height=200)

if st.button("Run Diagnostic"):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
    elif not workflow_data:
        st.warning("Please provide workflow data to analyze.")
    else:
        with st.spinner("Analyzing shopflow..."):
            try:
                model = genai.GenerativeModel('gemini-pro')
                prompt = f"Analyze the following shopflow/workflow data and provide a diagnostic report with identified bottlenecks and optimization suggestions:\n\n{workflow_data}"
                response = model.generate_content(prompt)
                st.subheader("Diagnostic Results")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
