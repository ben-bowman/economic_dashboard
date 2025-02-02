# 📊 U.S. Economic Dashboard

[![Streamlit Cloud](https://img.shields.io/badge/Live%20Demo-Streamlit-brightgreen)](https://bens-econ-dash.streamlit.app/)

This **Streamlit-powered dashboard** provides **real-time U.S. economic insights** by fetching and visualizing **GDP Growth, Unemployment Rate, and Inflation Rate** using data from:
- 📊 **FRED (Federal Reserve Economic Data)**
- 📈 **BLS (Bureau of Labor Statistics)**

## 🚀 Features
- **📈 Interactive Economic Indicators** – View **GDP Growth, Unemployment, and Inflation Trends** dynamically.
- **🔍 Customizable Filters** – Adjust the **year range and indicators** using an interactive sidebar.
- **🛠 Robust API Handling** – Handles **FRED & BLS API rate limits** with error detection and safe exits.
- **📉 Recession Shading** – Highlights **U.S. recessions** using historical data.
- **💾 Download Data** – Export the data table as a **CSV file**.
- **🎨 Beautiful Plotly Interactive Charts** – Hover, zoom, and explore the data visually.
- **☁️ Hosted on Streamlit Cloud** – Always available, no local setup required!

## 🌐 **Live App**
🔗 **[Visit the U.S. Economic Dashboard](https://bens-econ-dash.streamlit.app/)**

---

## 🛠 **How It Works**
### **1️⃣ Fetching Data from Two APIs**
The dashboard **retrieves real-time economic data** from two major government APIs:
- **FRED API** (Federal Reserve): Fetches **GDP Growth** and **Inflation Rate**.
- **BLS API** (Bureau of Labor Statistics): Fetches the **Unemployment Rate**.

### **2️⃣ Handling API Limitations**
- **Pagination & Data Handling** – The dashboard **automatically processes** multiple API requests efficiently.
- **Error Handling for Rate Limits** – If the **daily request limit is reached**, the dashboard **displays an error and stops** instead of breaking.

### **3️⃣ Sidebar Controls**
You can **customize your view** using the sidebar:
- 📆 **Year Range Selector** – Adjust the timeline for economic data.
- ✅ **Toggle Indicators** – Show or hide **GDP Growth, Inflation, and Unemployment** dynamically.
- 📉 **Highlight Recessions** – Toggle shading for historical **U.S. recession periods**.

### **4️⃣ Downloadable Data**
Want to analyze the data yourself?  
- Click the **Download CSV** button to **export the dataset**.

---

## 🛠 Deployment on Streamlit Cloud
To deploy this project yourself:

### 1️⃣ Clone the Repo & Install Dependencies
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
pip install -r requirements.txt
