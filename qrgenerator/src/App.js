import React, { useState } from "react";
import FileUpload from "./components/FileUpload ";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

function App() {
  const [message, setMessage] = useState("");

  const handleSetMessage = (msg) => {
    setMessage(msg);
  };

  return (
    <div className="App">
      <FileUpload setMessage={handleSetMessage} />
    </div>
  );
}

export default App;
