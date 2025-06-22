# Codeforces Problem Recommendation System

A web-based Codeforces Problem Recommendation System that suggests personalized coding problems to users based on their Codeforces submission history and skillset. Built using **React.js (Frontend)** and **Flask (Backend)** with **Machine Learning (TF-IDF + Cosine Similarity)** for recommendation logic.

---

## 🔍 Features

- 🔑 **Username Validation** (Checks if Codeforces username exists)
- 📝 **Problem Recommendations** based on:
  - Mode of rating (most solved rating)
  - Weak and Strong Tags (calculated from user’s submission history)
- 📜 **Submission History** (displays recent submission verdicts)
- ❌ Shows errors for invalid usernames or empty histories
- 🌍 Fully deployed and accessible via web URL
- 💾 **Fully In-Memory Backend** (no per-user CSV files)
- ⚡️ Backend fetches fresh data from Codeforces API
- ✅ React + Flask single unified deployment (via Render.com)

---

## 📦 Tech Stack

| Layer      | Technology                    |
|-----------|-------------------------------|
| Frontend  | React.js (with Context API)    |
| Backend   | Python Flask + Flask-CORS      |
| Machine Learning | TF-IDF, Cosine Similarity |
| External  | Codeforces Public API          |
| Deployment| Render.com                     |

---

## 📂 Project Structure

/backend
│ ├── app.py # Flask backend (in-memory)
│ ├── codeforces_problems.csv # Base dataset
│ ├── requirements.txt
│ └── build/ # Frontend React build moved here
│
/frontend
│ ├── src/
│ │ ├── App.js
│ │ ├── index.js
│ │ ├── UserContext.js
│ │ ├── components/
│ │ │ └── Navbar.js
│ │ └── pages/
│ │ ├── Home.js
│ │ ├── Problems.js
│ │ └── History.js
│ └── package.json
│
└── README.md


---

## 🚀 Deployment Guide (Render.com)

1. **Backend Setup (Render.com):**
   - Set environment variables:
     ```
     PYTHON_VERSION = 3.x
     ```
   - `requirements.txt` includes:
     ```
     Flask
     Flask-Cors
     pandas
     scikit-learn
     requests
     gunicorn
     ```
   - In **Render Build Command**:  
     ```
     pip install -r requirements.txt
     ```
   - In **Render Start Command**:  
     ```
     gunicorn app:app
     ```

2. **Frontend Setup:**
   - Run:
     ```
     npm run build
     ```
   - Move `/frontend/build` folder to `/backend/`.

3. **Automatic serving from Flask app.py**:
   ```python
   app = Flask(__name__, static_folder="build", static_url_path="/")
   
   @app.route('/', defaults={'path': ''})
   @app.route('/<path:path>')
   def serve(path):
       if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
           return send_from_directory(app.static_folder, path)
       else:
           return send_from_directory(app.static_folder, 'index.html')
