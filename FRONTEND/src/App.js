import "./App.css";
import { useState, useEffect } from "react";

function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [list, setList] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState("daily");
  const handleStockSelection = (symbol) => setSelectedStock(symbol);
  const userId = "user1";
  // const url = `https://mcsbt-integration-416418.ew.r.appspot.com`;
  const url = `http://127.0.0.1:5001`;

  useEffect(() => {
    async function fetchData() {
      await fetch(`${url}/api/portfolio`)
        .then((response) => response.json())
        .then((data) => {
          console.log("Fetched portfolio data:", data);
          setList(data); // Update the state with the fetched data
        })
        .catch((error) => {
          console.error("Error fetching data:", error);
          // If there's an error, i set some error state and display it
        });
    }
    fetchData();
  }, []);

  console.log(`got data ${list}`);
  const [stockDetails, setStockDetails] = useState(null);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome, {userId}</h1>
      </header>
      <main>
        {error && <div className="Error-message">{error}</div>}
        {list ? (
          <div>
            <h2 className="Portfolio-value">
              Total Portfolio Value: ${list.total_port_val}
            </h2>
            <section className="Stock-list">
              {Object.entries(list.stocks).map(([symbol, stockInfo]) => (
                <div className="Stock-item" key={symbol}>
                  <h3>{symbol}</h3>
                  <p>
                    {stockInfo.num_stocks} stocks at ${stockInfo.last_close}
                  </p>
                  <button
                    className="Select-button"
                    onClick={() => handleStockSelection(symbol)}
                  >
                    Select
                  </button>
                </div>
              ))}
            </section>
          </div>
        ) : (
          <div>Loading portfolio...</div>
        )}
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} DebuggingDollars</p>
      </footer>
    </div>
  );
}

export default App;
