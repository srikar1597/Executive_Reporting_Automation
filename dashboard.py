import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os
from dotenv import load_dotenv
from together import Together

# Load API Key from .env
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

# Initialize Together client
client = Together(api_key=together_api_key)

# Streamlit UI setup
st.set_page_config(page_title="Executive AI Dashboard", layout="wide")
st.title("📊 Executive AI Dashboard")
st.markdown("Automated board reports, KPI tracking, AI-generated strategic insights, and interactive visualizations.")

# File upload
uploaded_file = st.file_uploader("📁 Upload KPI or Metrics File (CSV/Excel)", type=["csv", "xlsx"])
df = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.success("✅ Data Loaded Successfully")
    except Exception as e:
        st.error(f"❌ File Error: {e}")

# Show data and auto-generate visuals
if df is not None:
    st.subheader("📈 Uploaded Data Preview")
    st.dataframe(df, use_container_width=True)

    numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    # Section: Visualizations
    st.markdown("## 📊 Auto-Generated KPI Visualizations")

    # Line charts for time series or metrics
    for col in numeric_columns:
        st.markdown(f"### 📈 Trend Line for **{col}**")
        fig = px.line(df, y=col, title=f"Trend of {col}")
        st.plotly_chart(fig, use_container_width=True)

    # Bar charts
    for col in numeric_columns:
        st.markdown(f"### 📊 Bar Chart for **{col}**")
        fig = px.bar(df, y=col, title=f"Distribution of {col}")
        st.plotly_chart(fig, use_container_width=True)

    # Pie chart for first categorical column
    if categorical_columns:
        st.markdown(f"### 🎯 Pie Chart of **{categorical_columns[0]}**")
        pie_data = df[categorical_columns[0]].value_counts().reset_index()
        pie_data.columns = [categorical_columns[0], "Count"]
        fig = px.pie(pie_data, names=categorical_columns[0], values="Count", title=f"Distribution of {categorical_columns[0]}")
        st.plotly_chart(fig, use_container_width=True)

    # Correlation heatmap
    if len(numeric_columns) >= 2:
        st.markdown("### ♨️ Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # AI Report Generation
    st.markdown("## 🧠 AI-Generated Executive Report")
    user_instruction = st.text_area(
        "✍️ Optional Custom Prompt:",
        value=" Analyze KPIs, summarize performance, detect trends, suggest actions, and highlight risks and opportunities."
    )

    if st.button("📌 Generate Report"):
        with st.spinner("🚀 Generating detailed executive report..."):

            sample_data = df.head(15).to_csv(index=False)
            prompt = f"""
You are a highly experienced executive AI analyst. Based on the following top 15 rows of KPI data, generate a full board report with the following structure:

1. Executive Summary: A concise summary of the business performance.
2. KPI Analysis: Key findings, trends, highs and lows in the data.
3. Strategic Recommendations: Actionable insights and suggestions.
4. Risks and Opportunities: Highlight any risks or growth potential.

Data:
{sample_data}

Instruction:
{user_instruction}
"""

            try:
                response = client.chat.completions.create(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    messages=[
                        {"role": "system", "content": "You are an expert board report generator and business intelligence analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7,
                    top_p=0.9
                )

                full_response = response.choices[0].message.content
                st.success("✅ Executive Report Ready")
                st.markdown("### 📋 Full AI-Generated Report")
                st.markdown(full_response)

            except Exception as e:
                st.error(f"❌ Together API Error: {e}")

else:
    st.info("📂 Please upload a CSV or Excel file to begin.")

# Footer
st.markdown("---")
st.caption("Built with 💡 Together AI + Streamlit | Executive AI Dashboard © 2025")
