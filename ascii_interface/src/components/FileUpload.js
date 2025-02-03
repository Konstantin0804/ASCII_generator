import React, { useState } from "react";
import API_URL from "../config";

function FileUpload({ setAsciiArt }) {
  const [file, setFile] = useState(null);
  const [height, setHeight] = useState(50);
  const [asciiChars, setAsciiChars] = useState("");
  const [word, setWord] = useState("");
  const [textPosition, setTextPosition] = useState("MID_CENTER");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("height", height);
    formData.append("ascii_chars", asciiChars);
    formData.append("word", word);
    formData.append("text_position", textPosition);

    try {
      const response = await fetch(`${API_URL}/`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setAsciiArt(data.ascii_art);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} required />
      <input type="number" value={height} onChange={(e) => setHeight(e.target.value)} min="10" max="200" />
      <input type="text" placeholder="ASCII Characters (optional)" value={asciiChars} onChange={(e) => setAsciiChars(e.target.value)} />
      <input type="text" placeholder="Insert Word (optional)" value={word} onChange={(e) => setWord(e.target.value)} />
      <select value={textPosition} onChange={(e) => setTextPosition(e.target.value)}>
        <option value="TOP_LEFT">Top Left</option>
        <option value="TOP_CENTER">Top Center</option>
        <option value="TOP_RIGHT">Top Right</option>
        <option value="MID_LEFT">Middle Left</option>
        <option value="MID_CENTER">Middle Center</option>
        <option value="MID_RIGHT">Middle Right</option>
        <option value="LOW_LEFT">Bottom Left</option>
        <option value="LOW_CENTER">Bottom Center</option>
        <option value="LOW_RIGHT">Bottom Right</option>
      </select>
      <button type="submit">Convert to ASCII</button>
    </form>
  );
}

export default FileUpload;