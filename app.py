import streamlit as st
import os
import requests
import json

# Page Configuration for Mobile Viewports
st.set_page_config(page_title="ShopFlow AI", page_icon="⚡", layout="centered")

st.title("⚡ ShopFlow AI Diagnostic Portal")
st.write("Master Technical Circuit & Sensor Analytics")

# --- Form Inputs ---
with st.form("diagnostic_form"):
    target_vin = st.text_input("Target VIN", value="1HGFC2F76H3011245")
    active_dtcs = st.text_input("Active DTCs", value="P0101, P0113")
    symptoms = st.text_area("Customer Symptoms", value="Hesitation on acceleration, sluggish response")
    tech_notes = st.text_area("Technician Notes / Scope Readings", value="Checked 5V reference line at the MAF connector, measures 5.01V. Ground line voltage drop test reads 30mV. Signal wire output at idle sits steady at 1.2V but doesn't sweep smoothly when snap-throttled.")
    
    submit_button = st.form_submit_button("Run Master Circuit Diagnostic")

def decode_vin_free(vin):
    if len(vin) != 17: return None
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin}?format=json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get("Results", [])
            year = next((i["Value"] for i in results if i["Variable"] == "Model Year"), "N/A")
            make = next((i["Value"] for i in results if i["Variable"] == "Make"), "N/A")
            model = next((i["Value"] for i in results if i["Variable"] == "Model"), "N/A")
            engine = next((i["Value"] for i in results if i["Variable"] == "Displacement (L)"), "N/A")
            return {"year": year, "make": make, "model": model, "engine": engine}
    except: pass
    return None

if submit_button:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        st.error("Missing API Key configuration in settings.")
        st.stop()
        
    with st.spinner("Decoding vehicle parameters and analyzing live scope data..."):
        specs = decode_vin_free(target_vin) or {"year": "N/A", "make": "N/A", "model": "N/A", "engine": "N/A"}
        year, make, model, engine = specs["year"], specs["make"], specs["model"], specs["engine"]
        
        st.success(f"🚗 IDENTIFIED: {year} {make} {model} ({engine}L)")
        
        prompt = f"""
        You are an expert master automotive diagnostic assistant. Analyze this shop repair order:
        VEHICLE: {year} {make} {model} {engine}
        VIN: {target_vin}
        ACTIVE DTCS: {active_dtcs}
        CUSTOMER SYMPTOMS: {symptoms}
        TECHNICIAN SCOPE/LIVE NOTES: {tech_notes}
        
        Provide a professional electrical testing strategy. Focus on sensor circuit verification, pinout isolation targets, and step-by-step voltage drop or scope measurement thresholds.
        """
        
        # Direct REST API call to support new AQ. keys natively
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                res_json = res.json()
                text_output = res_json["candidates"][0]["content"]["parts"][0]["text"]
                st.subheader("⚡ TARGETED CIRCUIT ANALYSIS & DIAGNOSTIC TREE")
                st.write(text_output)
            else:
                st.error(f"Brain Sync Error (HTTP {res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Network Error: {e}")
