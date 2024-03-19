import "./App.css";
import { useState, useEffect } from "react";

function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState("");
  const [list, setList] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);
  const [selectedInterval, setSelectedInterval] = useState("daily");
  const [stockToAdd, setStockToAdd] = useState(""); // State to manage stock input
  const [quantityToAdd, setQuantityToAdd] = useState(""); // State to manage quantity input
  const userId = "user1";
  const url = `http://127.0.0.1:5001`;

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(`${url}/api/portfolio`);
        const data = await response.json();
        console.log("Fetched portfolio data:", data);
        setList(data); // Update the state with the fetched data
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data.");
      }
    }
    fetchData();
  }, []);

  const handleStockSelection = (symbol) => setSelectedStock(symbol);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const userId = "1"; // This should be retrieved from a logged-in user session or state
    try {
      const response = await fetch(`${url}/api/portfolio/update_user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          symbol: stockToAdd.toUpperCase(), // Symbols are usually uppercase
          quantity: parseInt(quantityToAdd, 10), // Ensure the quantity is an integer
        }),
      });
      const data = await response.json();
      if (response.ok) {
        console.log("Stock updated:", data);
        // Optionally reset the form fields and fetch the updated list
        setStockToAdd("");
        setQuantityToAdd("");
        // Trigger a refresh of your portfolio state to reflect the updated data
        // You might need a new useEffect or a function that re-fetches the portfolio data
      } else {
        // Handle any errors from the server side
        setError(data.error || "An error occurred while updating the stock.");
      }
    } catch (error) {
      console.error("Error updating stock:", error);
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
        <p>&copy; {new Date().getFullYear()} Floos</p>
      </footer>
    </div>
  );
}

export default App;
