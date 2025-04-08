import os
import json
import time
import streamlit as st
from google import genai
from pyvis.network import Network
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={'api_version': 'v1alpha'}
)

# Streamlit UI
st.set_page_config(page_title="Roadmap Generator", layout="wide")
st.title("Using NLP and LLM/Model Roadmap Generator 🚀")
st.write("Generate a roadmap for any topic using AI and visualize it as an interactive graph.")

# Sidebar Customization
st.sidebar.header("🛠️ Graph Customization")
topic = st.sidebar.text_input("📘 Enter Topic", value="Machine Learning")
node_color = st.sidebar.color_picker("🎨 Node Color", "#1f78b4")
edge_color = st.sidebar.color_picker("🔗 Edge Color", "#ffffff")
node_size = st.sidebar.slider("🔵 Node Size", 10, 100, 30)
font_size = st.sidebar.slider("🔠 Font Size", 10, 40, 20)
layout_type = st.sidebar.selectbox("📐 Layout Type", ["barnes_hut", "repulsion"])

if st.sidebar.button("🚀 Generate Roadmap"):
    with st.spinner("Generating roadmap... Please wait ⏳"):
        # Step 1: Generate roadmap content
        prompt = f"Create a detailed roadmap of {topic}, including subjects, algorithms, steps, and types."
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        initial_data = response.text.strip()

        # Step 2: Ask Gemini to structure JSON
        json_prompt = (
            f"Convert this roadmap into a valid JSON with:\n"
            f"- 'nodes': a list of dictionaries with 'id' and 'label'.\n"
            f"- 'edges': a list of dictionaries with 'source', 'target', and 'relation'.\n"
            f"Only return valid JSON without explanations.\n\n"
            f"Roadmap Data:\n{initial_data}"
        )

        json_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=json_prompt
        )

        json_data = json_response.text.strip()

        if json_data.startswith("```json"):
            json_data = json_data[7:].strip()
        if json_data.endswith("```"):
            json_data = json_data[:-3].strip()

        try:
            roadmap_data = json.loads(json_data)
        except json.JSONDecodeError:
            st.error("❌ Failed to generate valid JSON. Try again.")
            st.stop()

        # Step 3: Create PyVis graph
        g = Network(height="750px", width="100%", bgcolor="#f9f9f9", font_color="black", directed=True)

        if layout_type == "barnes_hut":
            g.barnes_hut()
        else:
            g.repulsion()

        for node in roadmap_data["nodes"]:
            g.add_node(
                node["id"],
                label=node["label"],
                title=node["label"],
                color=node_color,
                size=node_size,
                font={"size": font_size, "color": "black"}
            )

        for edge in roadmap_data["edges"]:
            g.add_edge(
                edge["source"],
                edge["target"],
                title=edge["relation"],
                color=edge_color,
                width=2,
                arrows="to"
            )

        # Generate and display HTML
        html = g.generate_html()
        components.html(html, height=800, scrolling=True)

        st.success("✅ Roadmap generated successfully!")
