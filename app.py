import os
import json
import time
import webbrowser
import streamlit as st
from google import genai
from pyvis.network import Network
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),  # Set API key in .env or replace here
    http_options={'api_version': 'v1alpha'}
)

# Streamlit UI
st.title("Using NlP and LLM/model Roadmap Generator 🚀")
st.write("Generate a roadmap for any topic using AI and visualize it as an interactive graph.")

# User input for topic
topic = st.text_input("Enter the topic for the roadmap", "Machine Learning")

if st.button("Generate Roadmap"):
    with st.spinner("Generating roadmap... Please wait ⏳"):

        # Step 1: Generate roadmap details
        prompt = f"Create a detailed roadmap of {topic}, including subjects, algorithms, steps, and types."
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )

        initial_data = response.text.strip()

        # Step 2: Convert roadmap to structured JSON
        json_prompt = (
            f"Convert this roadmap into a valid JSON with:\n"
            f"- 'nodes': a list of dictionaries with 'id' and 'label'.\n"
            f"- 'edges': a list of dictionaries with 'source', 'target', and 'relation'.\n"
            f"Ensure the JSON is valid and contains no extra explanations.\n\n"
            f"Roadmap Data:\n{initial_data}"
        )

        retry_count = 3  # Retry in case of invalid JSON
        roadmap_data = None

        for attempt in range(retry_count):
            json_response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=json_prompt
            )

            json_data = json_response.text.strip()

            # Remove markdown artifacts
            if json_data.startswith('```json'):
                json_data = json_data[7:].strip()
            if json_data.endswith('```'):
                json_data = json_data[:-3].strip()

            try:
                roadmap_data = json.loads(json_data)
                break  # Successfully parsed JSON, exit loop
            except json.JSONDecodeError:
                st.warning(f"Attempt {attempt+1}: Received invalid JSON. Retrying...")
                time.sleep(2)

        if roadmap_data is None:
            st.error("Error: Failed to generate a valid roadmap. Please try again.")
            st.stop()

        # Save JSON data
        with open('roadmap_data.json', 'w') as f:
            json.dump(roadmap_data, f, indent=4)

        # Step 3: Generate visualization with PyVis
        g = Network(height="1500px", width="100%", bgcolor="#222222", font_color="white", directed=True)

        # Add nodes
        for node in roadmap_data['nodes']:
            g.add_node(node["id"], label=node["label"], title=node["label"], color="blue")

        # Add edges
        for edge in roadmap_data['edges']:
            g.add_edge(edge["source"], edge["target"], title=edge["relation"], color="white")

        # Apply layout
        g.barnes_hut()

        # Save the roadmap visualization
        g.save_graph('roadmap.html')

        st.success("Roadmap generated successfully!")

# Button to open the visualization
if os.path.exists('roadmap.html'):
    if st.button("Open Roadmap Visualization"):
        webbrowser.open('roadmap.html')
