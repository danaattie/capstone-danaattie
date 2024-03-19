import "./App.css";
import { useState, useEffect } from "react";

function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [list, setList] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [historicalPrices, setHistoricalPrices] = useState([]);
  const [stockToAdd, setStockToAdd] = useState(""); //manage stock input
  const [quantityToAdd, setQuantityToAdd] = useState(""); //state to manage quantity input
  const userId = "user1";
  const url = `http://127.0.0.1:5001`;

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`${url}/api/portfolio`);
        const data = await response.json();
        console.log("Fetched portfolio data:", data);
        setList(data); //to update the state with the fetched data
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data.");
      }
    }
    fetchData();
  }, []);

  const handleStockSelection = async (symbol) => {
    setSelectedStock(symbol);
    setError("");
    try {
      const response = await fetch(`${url}/api/historical_prices/${symbol}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const pricesData = await response.json();
      setHistoricalPrices(pricesData); // Assuming pricesData is already an array
    } catch (error) {
      setError("Failed to fetch historical prices.");
    }
  };

  const fetchHistoricalPrices = async (symbol) => {
    setError("");
    try {
      const response = await fetch(`${url}/api/historical_prices/${symbol}`);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const pricesData = await response.json();
      setHistoricalPrices(pricesData);
    } catch (error) {
      console.error("Error fetching historical prices:", error);
      setError("Failed to fetch historical prices.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${url}/api/portfolio/update_user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          symbol: stockToAdd.toUpperCase(),
          quantity: parseInt(quantityToAdd, 10),
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setStockToAdd("");
        setQuantityToAdd("");
        //update the list to reflect the new changes
        setList(data);
      } else {
        setError(data.error || "An error occurred while updating the stock.");
      }
    } catch (error) {
      setError("Failed to update stock. Please try again.");
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome, {userId}</h1>
      </header>
      <main>
        {error && <div className="Error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Stock Symbol"
            value={stockToAdd}
            onChange={(e) => setStockToAdd(e.target.value)}
          />
          <input
            type="number"
            placeholder="Quantity"
            value={quantityToAdd}
            onChange={(e) => setQuantityToAdd(e.target.value)}
          />
          <button type="submit">Add Stock</button>
        </form>
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
                    className="Data-button"
                    onClick={() => handleStockSelection(symbol)}
                  >
                    Data
                  </button>
                  {selectedStock === symbol && historicalPrices.length > 0 && (
                    <table>
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Close Price</th>
                        </tr>
                      </thead>
                      <tbody>
                        {historicalPrices.map((price, index) => (
                          <tr key={index}>
                            <td>{Object.keys(price)[0]}</td>
                            <td>${Object.values(price)[0]}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              ))}
            </section>
          </div>
        ) : (
          <div>Loading portfolio...</div>
        )}
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} Floos</p>
      </footer>
    </div>
  );
}

export default App;
