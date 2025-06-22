
import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserContext } from "../UserContext";
import axios from "axios";

function Home() {
  const [inputUsername, setInputUsername] = useState("");
  const { setUsername } = useContext(UserContext);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = () => {
    if (inputUsername.trim() === "") {
      setError("Please enter a username.");
      return;
    }

    // Check if username exists via backend API before navigating
    // axios.get(`http://127.0.0.1:5000/recommend?username=${inputUsername}`)
    axios.get(`/recommend?username=${inputUsername}`)
      .then(() => {
        setError("");
        setUsername(inputUsername);
        navigate("/problems");
      })
      .catch((err) => {
        if (err.response && err.response.status === 400) {
          setError("Invalid username. Please try again.");
        } else if (err.response && err.response.status === 404) {
          setError("No submissions found for this user.");
        } else {
          setError("Server error. Please try later.");
        }
      });
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Codeforces Recommender</h1>
      <input
        type="text"
        placeholder="Enter Codeforces Username"
        value={inputUsername}
        onChange={(e) => setInputUsername(e.target.value)}
        style={{ padding: "10px", fontSize: "16px" }}
      />
      <button onClick={handleSubmit} style={{ marginLeft: "10px", padding: "10px", fontSize: "16px" }}>
        Submit
      </button>
      {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}
    </div>
  );
}

export default Home;
