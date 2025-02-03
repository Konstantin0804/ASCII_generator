import React, { useState } from "react";
import AsciiForm from "./components/AsciiForm";  // Импортируем компонент формы
import AsciiOutput from "./components/AsciiOutput";
import "./styles.css";

function App() {
  const [asciiArt, setAsciiArt] = useState(""); // Храним ASCII-арт
  const [cols, setCols] = useState(0); // Число столбцов
  const [rows, setRows] = useState(0); // Число строк

  // Функция для обработки данных, отправленных с формы
  const handleAsciiArt = (asciiData, colsData, rowsData) => {
    setAsciiArt(asciiData);
    setCols(colsData);
    setRows(rowsData);
  };

  return (
    <div className="container">
      <h1>ASCII Art Converter</h1>  {/* Заголовок только здесь */}
      <AsciiForm setAsciiArt={handleAsciiArt} />  {/* Используем компонент формы */}
      <AsciiOutput asciiArt={asciiArt} cols={cols} rows={rows} /> {/* Выводим результат */}
    </div>
  );
}

export default App;