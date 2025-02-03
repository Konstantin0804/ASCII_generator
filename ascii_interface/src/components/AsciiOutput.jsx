// AsciiOutput.js
import React from "react";

function AsciiOutput({ asciiArt, cols, rows }) {
  return (
    <div className="output-container">
      <h2>ASCII Art Output:</h2>
      <textarea
        id="asciiOutput"
        readOnly
        rows={rows}
        cols={cols}
        value={asciiArt}
      />
    </div>
  );
}

export default AsciiOutput;