# 📊 U.S. Economic Dashboard

This Streamlit app visualizes key U.S. economic indicators such as **GDP Growth, Unemployment Rate, and Inflation Rate** using real-time data from **FRED (Federal Reserve Economic Data) and BLS (Bureau of Labor Statistics).**

## 🚀 Features
- 📈 Interactive **GDP, Unemployment, and Inflation Trends**
- 📊 State-wise Unemployment Comparison
- 🔎 Filter by **Year & Economic Indicator**
- 🎨 Beautiful **Plotly Interactive Charts**
- 🌐 **Deployed on Streamlit Cloud**

---

## 🛠 Deployment on Streamlit Cloud
To deploy this project on **Streamlit Community Cloud**:

### 1️⃣ Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2️⃣ Set Up Streamlit Secrets
- Go to **Streamlit Cloud** → Select **"Manage App"**.
- Click **"Secrets"** and **add your API keys manually**:
  ```
  FRED_API_KEY = "YOUR_FRED_API_KEY"
  BLS_API_KEY = "YOUR_BLS_API_KEY"
  ```
- Save the secrets.

### 3️⃣ Deploy the App
- Go to [Streamlit Cloud](https://share.streamlit.io/) and connect your GitHub repo.
- Select `dashboard.py` as the main script.
- Click **Deploy** 🚀

Your app will be live at:
```
https://your-app-name.streamlit.app
```

---

## 📝 License
This project is **MIT Licensed** – free to use, modify, and share.

---

🎉 **Happy coding!** Let me know if you need help!
