import React, { useContext, useEffect, useState } from "react";
import axios from "axios";
import { UserContext } from "../UserContext";

function Problems() {
  const { username } = useContext(UserContext);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (username) {
      // axios.get(`http://127.0.0.1:5000/recommend?username=${username}`)
      axios.get(`/recommend?username=${username}`)
        .then((res) => setData(res.data))
        .catch((err) => setError("Error fetching recommendations."));
    }
  }, [username]);

  if (!username) return <p style={{ color: "red" }}>No username provided.</p>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>Problem Recommendations for {username}</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {data ? (
        <ul>
          {data.recommendations.map((prob, index) => (
            <li key={index}>
              {prob.name} - Rating: {prob.rating} - Tags: {prob.tags.join(", ")}
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading recommendations...</p>
      )}
    </div>
  );
}

export default Problems;
