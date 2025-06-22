import pandas as pd
import ast
import os
import requests
from collections import defaultdict
from flask import Flask, request, jsonify, send_from_directory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__, static_folder="build", static_url_path="/")  # ✅ Corrected for deployment
CORS(app)

# Load problems dataset once at startup
df_problems = pd.read_csv("codeforces_problems.csv")
df_problems['tags'] = df_problems['tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
df_problems['rating'] = pd.to_numeric(df_problems['rating'], errors='coerce')
df_problems['rating'] = df_problems['rating'].fillna(df_problems['rating'].median())

# ============================ 1. CHECK IF USER EXISTS ============================
def check_user_exists(username):
    url = f"https://codeforces.com/api/user.info?handles={username}"
    response = requests.get(url)
    return response.status_code == 200 and response.json().get("status") == "OK"

# ============================ 2. FETCH USER SUBMISSIONS (In-Memory) ============================
def fetch_user_submissions(username):
    url = f"https://codeforces.com/api/user.status?handle={username}"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "OK":
        return None

    submissions = data["result"]
    processed_data = []

    for sub in submissions:
        problem = sub["problem"]
        processed_data.append({
            "contest_id": problem.get("contestId", "Practice"),
            "problem_index": problem["index"],
            "name": problem["name"],
            "tags": problem.get("tags", []),
            "rating": problem.get("rating", "Unknown"),
            "verdict": sub["verdict"],
            "time": sub["creationTimeSeconds"]
        })

    df_user = pd.DataFrame(processed_data)
    if df_user.empty:
        return None

    return df_user

# ============================ 3. CALCULATE ACCURACY ============================
def calculate_accuracy(df_user):
    tag_attempts = defaultdict(int)
    tag_solved = defaultdict(int)
    
    for _, row in df_user.iterrows():
        try:
            tags = row['tags'] if isinstance(row['tags'], list) else ast.literal_eval(row['tags'])
            for tag in tags:
                tag_attempts[tag] += 1
                if row['verdict'] == 'OK':  
                    tag_solved[tag] += 1
        except (ValueError, SyntaxError):
            continue  

    accuracy = {tag: tag_solved[tag] / tag_attempts[tag] if tag_attempts[tag] > 0 else 0 for tag in tag_attempts}
    return accuracy

# ============================ 4. CATEGORIZE STRENGTHS ============================
def categorize_strengths(accuracy):
    strong_tags = [tag for tag, acc in accuracy.items() if acc > 0.55]
    weak_tags = [tag for tag, acc in accuracy.items() if acc < 0.4]
    return strong_tags, weak_tags

# ============================ 5. RECOMMEND PROBLEMS ============================
def recommend_problems(df_user, weak_tags, strong_tags, mode_rating, num_recommendations=10):
    df_problems_copy = df_problems.copy()

    df_problems_copy['tags_str'] = df_problems_copy['tags'].apply(lambda x: ' '.join(x))
    df_user['tags_str'] = df_user['tags'].apply(lambda x: ' '.join(x) if isinstance(x, list) else ' '.join(ast.literal_eval(x)))

    vectorizer = TfidfVectorizer()
    problem_matrix = vectorizer.fit_transform(df_problems_copy['tags_str'])
    user_matrix = vectorizer.transform(df_user['tags_str'])

    similarity_scores = cosine_similarity(user_matrix, problem_matrix).mean(axis=0)
    df_problems_copy['similarity'] = similarity_scores
    df_problems_copy = df_problems_copy.sort_values(by='similarity', ascending=False)

    # Weak problems: rating == mode_rating
    weak_problems = df_problems_copy[
        (df_problems_copy['rating'] == mode_rating) &
        (df_problems_copy['tags'].apply(lambda tags: any(tag in weak_tags for tag in tags)))
    ].head(5)

    # Strong problems: rating == mode_rating+100 or mode_rating+200
    strong_problems = df_problems_copy[
        (df_problems_copy['rating'].isin([mode_rating + 100, mode_rating + 200])) &
        (df_problems_copy['tags'].apply(lambda tags: any(tag in strong_tags for tag in tags)))
    ].head(5)

    recommended_problems = pd.concat([weak_problems, strong_problems]).sample(frac=1).reset_index(drop=True)
    return recommended_problems

# ============================ 6. FLASK API ROUTES ============================

@app.route('/recommend', methods=['GET'])
def recommend():
    username = request.args.get('username')

    if not username or not check_user_exists(username):
        return jsonify({"error": "Invalid or missing username"}), 400
    
    df_user = fetch_user_submissions(username)
    if df_user is None or df_user.empty:
        return jsonify({"error": "No submissions found for this user"}), 404

    accuracy = calculate_accuracy(df_user)
    strong_tags, weak_tags = categorize_strengths(accuracy)

    # Calculate mode rating
    mode_rating = df_user[df_user['verdict'] == 'OK']['rating'].mode()
    if len(mode_rating) == 0 or pd.isna(mode_rating[0]):
        mode_rating = 0
    else:
        mode_rating = int(mode_rating[0])

    recommended_problems = recommend_problems(df_user, weak_tags, strong_tags, mode_rating)

    return jsonify({
        "mode_rating": mode_rating,
        "strong_topics": strong_tags,
        "weak_topics": weak_tags,
        "recommendations": recommended_problems.to_dict(orient="records")
    })

@app.route('/history', methods=['GET'])
def history():
    username = request.args.get('username')

    if not username or not check_user_exists(username):
        return jsonify({"error": "Invalid or missing username"}), 400
    
    df_user = fetch_user_submissions(username)
    if df_user is None or df_user.empty:
        return jsonify({"error": "No submissions found for this user"}), 404

    history_data = df_user[['contest_id', 'problem_index', 'name', 'tags', 'rating', 'verdict', 'time']].to_dict(orient='records')
    return jsonify({"history": history_data})

# ============================ 7. Serve React Frontend ============================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# ============================ 8. RUN FLASK APP ============================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=10000)
