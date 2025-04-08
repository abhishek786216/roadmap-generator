import os
import json
import time
import streamlit as st
import google.generativeai as genai
from pyvis.network import Network
from dotenv import load_dotenv
import streamlit.components.v1 as components
from io import StringIO
import base64

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(page_title="Roadmap Generator", layout="wide")

# Sidebar customization
st.sidebar.header("🎧 Customization")
topic = st.sidebar.text_input("📚 Enter Topic", value="Machine Learning")
node_color = st.sidebar.color_picker("🎨 Node Color", "#ADD8E6")
edge_color = st.sidebar.color_picker("🔗 Edge Color", "#FF5733")
node_size = st.sidebar.slider("🔵 Node Size", 10, 100, 34)
font_size = st.sidebar.slider("🌠 Font Size", 10, 40, 30)
layout_type = st.sidebar.selectbox("🧲 Layout", ["repulsion", "repulsion"])

st.title("Using NLP and LLM/Model Roadmap Generator 🚀")
st.write("Generate a roadmap for any topic using AI and visualize it as an interactive graph.")

# Generate roadmap
if st.sidebar.button("🚀 Generate Roadmap"):
    with st.spinner("Generating roadmap... Please wait ⌛"):
        prompt = f"Create a detailed roadmap of {topic}, including subjects, algorithms, steps, and types."
        response = model.generate_content(prompt)
        initial_data = response.text.strip()

        json_prompt = (
            f"Convert this roadmap into a valid JSON with:\n"
            f"- 'nodes': a list of dictionaries with 'id' and 'label'.\n"
            f"- 'edges': a list of dictionaries with 'source', 'target', and 'relation'.\n"
            f"Only return JSON.\n\n"
            f"Roadmap Data:\n{initial_data}"
        )

        roadmap_data = None
        for _ in range(3):
            json_response = model.generate_content(json_prompt)
            json_data = json_response.text.strip()
            if json_data.startswith("```json"):
                json_data = json_data[7:]
            if json_data.endswith("```"):
                json_data = json_data[:-3]
            try:
                roadmap_data = json.loads(json_data)
                break
            except json.JSONDecodeError:
                time.sleep(2)

        if roadmap_data is None:
            st.error("❌ Could not generate valid roadmap.")
            st.stop()

        with open("roadmap_data.json", "w") as f:
            json.dump(roadmap_data, f, indent=4)

        # Build PyVis graph
        g = Network(height="700px", width="100%", bgcolor="#f9f9f9", font_color="black", directed=True)

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
                font={"size": font_size, "face": "arial", "color": "black"}
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

        g.save_graph("roadmap.html")
        st.success("✅ Roadmap generated!")

        # Display graph
        st.subheader("📍 Interactive Roadmap")
        with open("roadmap.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=700, scrolling=True)

        # Download buttons
        st.subheader("🔧 Download Options")

        # Download JSON
        json_str = json.dumps(roadmap_data, indent=4)
        b64_json = base64.b64encode(json_str.encode()).decode()
        href_json = f'<a href="data:application/json;base64,{b64_json}" download="roadmap.json">Download JSON Roadmap 🔄</a>'
        st.markdown(href_json, unsafe_allow_html=True)

        # Download HTML
        with open("roadmap.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            b64_html = base64.b64encode(html_content.encode()).decode()
            href_html = f'<a href="data:text/html;base64,{b64_html}" download="roadmap.html">Download HTML File 📄</a>'
            st.markdown(href_html, unsafe_allow_html=True)
