import "./App.css";
import { useState, useEffect } from "react";

function App() {
  const [list, setList] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState("daily");
  const userId = "user1";
  const url = `http://127.0.0.1:5000/api/portfolio?userId=${userId}`;

  useEffect(() => {
    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        console.log("Portfolio data:", data);
        setList(data);
      })
      .catch((error) => console.error("Error fetching data:", error));
  }, [url]);

  // Function to handle when a stock is selected
  const handleStockSelection = (stockSymbol) => {
    setSelectedStock(stockSymbol);
    // You can add additional logic here if needed
  };

  // Function to handle interval change
  const handleIntervalChange = (newInterval) => {
    setSelectedInterval(newInterval);
    // You can add additional logic here if needed
  };

  return (
    <div className="App">
      <h1>Welcome, {userId}</h1>
      {list ? (
        <>
          <h2>Total Portfolio Value: ${list.total_port_val}</h2>
          <div>
            {Object.entries(list.portfolio).map(([symbol, stockInfo]) => (
              <div key={symbol}>
                <p>
                  {symbol}: {stockInfo.num_stocks} stocks at $
                  {stockInfo.last_close}
                </p>
                <button onClick={() => handleStockSelection(symbol)}>
                  Select
                </button>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p>Loading portfolio...</p>
      )}
      {selectedStock && (
        <div>
          <h3>Selected Stock: {selectedStock}</h3>
          <button onClick={() => handleIntervalChange("weekly")}>Weekly</button>
          <button onClick={() => handleIntervalChange("monthly")}>
            Monthly
          </button>
          {/* Add more interval buttons as needed */}
        </div>
      )}
    </div>
  );
}

export default App;
