import React, { useState, useEffect } from "react";
import "./App.css";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [list, setList] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [historicalPrices, setHistoricalPrices] = useState([]);
  const [stockToAdd, setStockToAdd] = useState("");
  const [quantityToAdd, setQuantityToAdd] = useState("");
  const userId = "user1";
  const url = `http://127.0.0.1:5001`;

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`${url}/api/portfolio`);
        const data = await response.json();
        console.log("Fetched portfolio data:", data);
        setList(data);
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
      setHistoricalPrices(pricesData);
    } catch (error) {
      setError("Failed to fetch historical prices.");
      console.error(error);
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
        setList(data);
      } else {
        setError(data.error || "An error occurred while updating the stock.");
      }
    } catch (error) {
      setError("Failed to update stock. Please try again.");
      console.error(error);
    }
  };

  // Function to prepare chart data
  const getChartData = () => {
    return {
      labels: historicalPrices.map((price) => Object.keys(price)[0]),
      datasets: [
        {
          label: `Historical Prices for ${selectedStock}`,
          data: historicalPrices.map((price) => Object.values(price)[0]),
          fill: false,
          backgroundColor: "rgb(75, 192, 192)",
          borderColor: "rgba(75, 192, 192, 0.2)",
        },
      ],
    };
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
        {list && (
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
                    <>
                      <Line data={getChartData()} />
                      <table>
                        <thead>
                          <tr>
                            <th>Date</th>
                            <th>Close Price</th>
                          </tr>
                        </thead>
                        <tbody>
                          {historicalPrices.map((price, index) => {
                            const [date, closePrice] = Object.entries(price)[0];
                            return (
                              <tr key={index}>
                                <td>{date}</td>
                                <td>${closePrice}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </>
                  )}
                </div>
              ))}
            </section>
          </div>
        )}
        {!list && <div>Loading portfolio...</div>}
      </main>
      <footer>
        <p>&copy; {new Date().getFullYear()} Floos</p>
      </footer>
    </div>
  );
}

export default App;
