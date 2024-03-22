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
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const url = `https://mcsbt-integration-416418.ew.r.appspot.com`;

  //function to fetch portfolio data
  const fetchPortfolioData = async () => {
    try {
      const response = await fetch(`${url}/api/portfolio`);
      const data = await response.json();
      console.log("Fetched portfolio data:", data);

      // to display the total portfolio value after logging in
      if (data.total_port_val) {
        console.log("Total Portfolio Value: ", data.total_port_val);
        setTotal(data.total_port_val);
      } else {
        console.log("No total portfolio value");
      }

      // for the purpose of displaying error messages
      setList(data);
    } catch (error) {
      console.error("Error fetching data:", error);
      setError("Failed to fetch data.");
    }
  };

  // fetching while logged in
  useEffect(() => {
    if (isLoggedIn) {
      fetchPortfolioData();
    }
  }, [isLoggedIn]);

  // data is sent between the front and back end
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${url}/login`, {
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (response.ok) {
        setIsLoggedIn(true);
        setError("");
        fetchPortfolioData();
      } else {
        setError("Login failed. Please check your username and password.");
      }
    } catch (error) {
      setError("Failed to log in. Please try again.");
      console.error(error);
    }
  };

  const handleLogout = async () => {
    try {
      //Send a request to the logout endpoint ; assigned but not used in the return statement as it implied many recurring errors
      const response = await fetch(`${url}/logout`, {
        credentials: "include", // Needed to include the session cookie
      });
      if (response.ok) {
        // Successfully logged out
        setIsLoggedIn(false);
        setPortfolio(null); //clear the portfolio state
        //clear any other state related to the authenticated user
      } else {
        //handle errors here, such as showing an error message to the user
        console.error("Logout failed");
      }
    } catch (error) {
      console.error("There was an error logging out", error);
    }
  };

  // stock data is sent
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
  // update/add/remove in the same button (precisions in main.py)
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${url}/api/portfolio/update_user`, {
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: 1, //assuming handle of user_id on the server-side based on authentication
          symbol: stockToAdd.toUpperCase(),
          quantity: parseInt(quantityToAdd, 10),
        }),
      });
      const data = await response.json();
      if (response.ok) {
        setStockToAdd("");
        setQuantityToAdd("");
        fetchPortfolioData();
      } else {
        setError(data.error || "An error occurred while updating the stock.");
      }
    } catch (error) {
      setError("Failed to update stock. Please try again.");
      console.error(error);
    }
  };
  // displaying historical prices
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

  // //display of login page
  if (!isLoggedIn) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>Please Log In</h1>
        </header>
        <main>
          {error && <div className="Error-message">{error}</div>}
          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit">Login</button>
          </form>
        </main>
      </div>
    );
  }

  // display after successful connection
  return (
    <div className="App">
      <header header className="App-header">
        <h1>Welcome to Floos</h1>
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
          <button type="submit">Update</button>
        </form>
        {list && (
          <div>
            <h2 className="Portfolio-value">Total Portfolio Value: ${total}</h2>
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
                            const date = Object.keys(price)[0];
                            const closePrice = Object.values(price)[0];
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
