import React, { useState, useEffect } from 'react';
import { ArrowUpDown, Info, Download } from 'lucide-react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import axios from 'axios';

interface StockData {
  rank: number;
  ticker: string;
  plot: string;
  performance: number;
}

const TopStocksPredicted: React.FC = () => {
  const [sortField, setSortField] = useState<keyof StockData>('rank');
  const [sortDirection, setSortDirection] = useState<'desc' | 'asc'>('asc');
  const [selectedRank, setSelectedRank] = useState<number | null>(null);

  const [stocksData, setStocksData] = useState<StockData[]>([{rank: 0, plot: "", ticker: "", performance: 0}]);

  useEffect(() => {
    axios.get('http://localhost:3000/topStocksPredicted')
    .then(response => {
      console.log(response.data);
      setStocksData(response.data);
      // console.log(correlatedStocksData);
    })
    .catch((error) => {
      console.error('Error fetching correlations:', error);
    });
  }, []);


  const sortedStocks = [...stocksData].sort((a, b) => {
    if (sortDirection === 'asc') {
      return a[sortField] > b[sortField] ? 1 : -1;
    } else {
      return a[sortField] < b[sortField] ? 1 : -1;
    }
  });

  const handleSort = (field: keyof StockData) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const getSortIcon = (field: keyof StockData) => {
    if (sortField === field) {
      return (
        <ArrowUpDown 
          className={`h-4 w-4 ml-1 inline-block transform ${sortDirection === 'asc' ? 'rotate-180' : ''}`} 
        />
      );
    }
    return <ArrowUpDown className="h-4 w-4 ml-1 inline-block opacity-30" />;
  };

    // Navigate to a specific page when a menu item is clicked
    const navigate = useNavigate(); // Initialize useNavigate
    const handleNavigation = (path: string) => {
      navigate(path); // Navigate to the path
    };

  return (
    <main className="max-w-7xl container mx-auto px-6 py-8 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Top Predicted Stocks in the Next Year</h1>
        {/* <div className="flex space-x-2">
          <button className="flex items-center px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100">
            <Info className="h-4 w-4 mr-1" />
            <span>Methodology</span>
          </button>
          <button className="flex items-center px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100">
            <Download className="h-4 w-4 mr-1" />
            <span>Export Data</span>
          </button>
        </div> */}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('rank')}
                >
                  <span className="flex items-center">
                    Rank {getSortIcon('rank')}
                  </span>
                </th>
                <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('ticker')}
                >
                  <span className="flex items-center">
                    Symbol {getSortIcon('ticker')}
                  </span>
                </th>
                {/* <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('ticker2')}
                >
                  <span className="flex items-center">
                    Symbol 2 {getSortIcon('ticker2')}
                  </span>
                </th> */}
                {/* <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('rank')}
                >
                  <span className="flex items-center">
                    Correlation {getSortIcon('correlation')}
                  </span>
                </th> */}
                {/* <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('sector')}
                >
                  <span className="flex items-center">
                    Sector {getSortIcon('sector')}
                  </span>
                </th> */}
                {/* <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('marketCap')}
                >
                  <span className="flex items-center">
                    Market Cap {getSortIcon('marketCap')}
                  </span>
                </th> */}
                <th 
                  scope="col" 
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                  onClick={() => handleSort('performance')}
                >
                  <span className="flex items-center">
                    Performance {getSortIcon('performance')}
                  </span>
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sortedStocks.map((stock) => (
                <tr 
                  key={stock.rank} 
                  className={`hover:bg-gray-50 ${selectedRank === stock.rank ? 'bg-blue-50' : ''}`}
                  onClick={() => setSelectedRank(stock.rank === selectedRank ? null : stock.rank)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {stock.rank}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">
                    <a href="#" onClick={(e) => {e.preventDefault(); handleNavigation(`/stock/${stock.ticker}`)}}>{stock.ticker}</a>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {stock.performance > 0 ? "+" : ""}{stock.performance.toFixed(2)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button className="text-blue-600 hover:text-blue-800 font-medium">
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedRank && (
        <div className="mt-8 bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">{stocksData[selectedRank - 1].ticker}</h2>
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
              Performance: {stocksData.find(s => s.rank === selectedRank)?.performance.toFixed(2)}%
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-3">Stock Chart</h3>
              <div className="h-100 border border-gray-200 rounded-lg p-4">
                <img src={`data:image/png;base64,${stocksData[selectedRank - 1].plot}`} />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-3">Stock Analysis</h3>
              <div className="space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Performance</h4>
                  <p className="text-sm text-gray-600">
                    {/* The beta of {stocksData[selectedRank - 1].ticker1} relative to {stocksData[selectedRank - 1].ticker2} is {stocksData.find(s => s.rank === selectedRank)?.beta.toFixed(2)}. 
                    This indicates that {stocksData[selectedRank - 1].ticker1} tends to move {stocksData.find(s => s.rank === selectedRank)?.beta.toFixed(2)} times 
                    the magnitude of {stocksData[selectedRank - 1].ticker2} in the same direction. */}
                    The price of {stocksData[selectedRank - 1].ticker} is projected to change by {stocksData[selectedRank - 1].performance > 0 ? "+" : ""}{stocksData[selectedRank - 1].performance.toFixed(2)}% over the next 365 days, compared to 365 trading days ago.
                  </p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Trading Strategy</h4>
                  <p className="text-sm text-gray-600">
                    {/* With a correlation of {stocksData.find(s => s.rank === selectedRank)?.correlation.toFixed(2)}, 
                    {stocksData[selectedRank - 1].ticker1} shows a strong positive relationship with {stocksData[selectedRank - 1].ticker2}. This suggests potential for pairs trading 
                    or using one stock as a leading indicator for the other. */}
                    The stock {stocksData[selectedRank - 1].ticker} is expected to experience significant growth, making it a strong investment opportunity. It is highly recommended to invest as soon as possible.
                  </p>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">Risk Assessment</h4>
                  <p className="text-sm text-gray-600">
                    {/* Holding both {stocksData[selectedRank - 1].ticker1} and {stocksData[selectedRank - 1].ticker2} may not provide optimal diversification due to their high correlation. 
                    Consider balancing your portfolio with assets that have lower correlation to these stocks. */}
                    The stock {stocksData[selectedRank - 1].ticker} presents a strong growth opportunity, making it an attractive investment. However, like any investment, it comes with inherent risks, including market volatility, company performance, and broader economic factors. While the potential for high returns is promising, investors should carefully assess these risks, stay informed on market trends, and consider a diversified strategy. 
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
};

export default TopStocksPredicted;