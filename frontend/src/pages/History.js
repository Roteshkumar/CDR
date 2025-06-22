import React, { useContext, useEffect, useState } from "react";
import axios from "axios";
import { UserContext } from "../UserContext";

function History() {
  const { username } = useContext(UserContext);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (username) {
      // axios.get(`http://127.0.0.1:5000/history?username=${username}`)
      axios.get(`/history?username=${username}`)
        .then((res) => setHistory(res.data.history))
        .catch(() => setError("Error fetching history."));
    }
  }, [username]);

  if (!username) return <p style={{ color: "red" }}>No username provided.</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>Submission History for {username}</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {history.length > 0 ? (
        <ul>
          {history.map((item, idx) => (
            <li key={idx}>
              {item.name} - Verdict: {item.verdict}
            </li>
          ))}
        </ul>
      ) : (
        <p>No history data found.</p>
      )}
    </div>
  );
}

export default History;
