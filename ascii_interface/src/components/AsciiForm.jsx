// AsciiForm.js
import React, { useState } from "react";

function AsciiForm({ setAsciiArt }) {
  const [file, setFile] = useState(null);
  const [height, setHeight] = useState(50);
  const [asciiChars, setAsciiChars] = useState("");
  const [word, setWord] = useState("");
  const [textPosition, setTextPosition] = useState("TOP_LEFT");

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("file", file);
    formData.append("height", height);
    formData.append("ascii_chars", asciiChars);
    formData.append("word", word);
    formData.append("text_position", textPosition);

    fetch("http://localhost:5000/", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setAsciiArt(data.ascii_art, data.cols, data.rows);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="file">Choose Image:</label>
        <input
          type="file"
          name="file"
          id="fileInput"
          required
          onChange={(e) => setFile(e.target.files[0])}
        />
      </div>
      <div className="form-group">
        <label htmlFor="height">Output Height:</label>
        <input
          type="number"
          name="height"
          value={height}
          min="10"
          max="200"
          onChange={(e) => setHeight(e.target.value)}
        />
      </div>
      <div className="form-group">
        <label htmlFor="ascii_chars">ASCII Characters:</label>
        <input
          type="text"
          name="ascii_chars"
          value={asciiChars}
          onChange={(e) => setAsciiChars(e.target.value)}
          placeholder="Optional, min 6 chars"
        />
      </div>
      <div className="form-group">
        <label htmlFor="word">Insert Word:</label>
        <input
          type="text"
          name="word"
          value={word}
          onChange={(e) => setWord(e.target.value)}
          placeholder="Optional"
        />
      </div>
      <div className="form-group">
        <label htmlFor="text_position">Text Position:</label>
        <select
          name="text_position"
          value={textPosition}
          onChange={(e) => setTextPosition(e.target.value)}
        >
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
      </div>
      <button type="submit">Convert to ASCII</button>
    </form>
  );
}

export default AsciiForm;