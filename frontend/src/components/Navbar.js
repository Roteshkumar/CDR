import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav style={{ padding: "10px", backgroundColor: "#333", color: "#fff" }}>
      <Link to="/" style={{ margin: "10px", color: "#fff" }}>Home</Link>
      <Link to="/problems" style={{ margin: "10px", color: "#fff" }}>Problem</Link>
      <Link to="/history" style={{ margin: "10px", color: "#fff" }}>History</Link>
    </nav>
  );
}

export default Navbar;
