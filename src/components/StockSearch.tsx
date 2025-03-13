import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';

function StockSearch() {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate(); // Hook for navigation

  // const stockList = ["NVDA", "TSLA", "AAPL"];

  const [stockList, setStockList] = useState(["NVDA", "TSLA", "AAPL"]);

  useEffect(() => {
    // Fetch the plot from the Node.js server
    axios.get('http://localhost:3000/tickers')  // Node.js server endpoint
      .then((response) => {
        setStockList(response.data.tickers);
      })
      .catch((error) => {
        console.error('Error fetching tickers:', error);
      });
  }, []);

  // Filter the stock list based on the search term
  const filteredStocks = stockList.filter(stock =>
    stock.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleStockClick = (stock: string) => {
    // Clear search bar
    setSearchTerm('');

    // Navigate to the stock detail page with the selected stock name
    navigate(`/stock/${stock}`);
  };

  return (
    <div className="relative w-64">
      <input
        type="text"
        placeholder="Search Stock"
        className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      {/* Dropdown menu */}
      {searchTerm && filteredStocks.length > 0 && (
        <ul className="absolute w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto z-20">
          {filteredStocks.map((stock, index) => (
            <li
              key={index}
              className="px-4 py-2 hover:bg-blue-100 cursor-pointer"
              // onClick={() => setSearchTerm(stock)}
              onClick={() => handleStockClick(stock)}
            >
              {stock}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default StockSearch;