import logo from "./logo.svg";
import "./App.css";
import { useEffect } from "react";

function App() {
  useEffect(() => {
    console.log("its Dana again");
    fetch("https://mcsbt-integration-416418.ew.r.appspot.com/api/portfolio")
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.error(error));
  }, []);
  return <div className="App">hello its Dana</div>;
}

export default App;
