import { useState, useEffect } from 'react';
import PlotComponent from '../components/PlotComponent';  // Import the PlotComponent
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface Option {
    id: number;
    label: string;
}

function Homepage() {
    let { stockSymbol = "NVDA" } = useParams();
    stockSymbol = stockSymbol.toUpperCase();

    // Array of options to select from
    const options: Option[] = [
      { id: 1, label: '200d SMA' },
      { id: 2, label: '50d SMA' },
      { id: 3, label: 'Predicted' },
      { id: 4, label: 'Buy Signals' },
      { id: 5, label: 'Sell Signals' },
    ];
  
    // State to keep track of selected options
    const [selectedOptions, setSelectedOptions] = useState<number[]>([3, 4, 5]);
  
    // Handle checkbox change
    const handleCheckboxChange = (id: number) => {
      setSelectedOptions((prevState) =>
        prevState.includes(id)
          ? prevState.filter((option) => option !== id) // Unselect if already selected
          : [...prevState, id] // Select the option
      );
    };

    // Get the list of selected options as strings (labels)
    const selectedLabels = options
    .filter((option) => selectedOptions.includes(option.id))
    .map((option) => option.label);

    // const correlatedStocksData = [
    //   { 
    //     symbol: 'MSFT', 
    //     name: 'Microsoft',
    //     correlation: 0.92,
    //     data: [
    //       { date: '2022', price: 110 },
    //       { date: '2023', price: 130 },
    //       { date: '2024', price: 150 },
    //       { date: '2025', price: 170 },
    //       { date: '2026', price: 190 },
    //       { date: '2027', price: 210 },
    //     ]
    //   },
    //   { 
    //     symbol: 'GOOGL', 
    //     name: 'Alphabet',
    //     correlation: 0.87,
    //     data: [
    //       { date: '2022', price: 105 },
    //       { date: '2023', price: 125 },
    //       { date: '2024', price: 145 },
    //       { date: '2025', price: 165 },
    //       { date: '2026', price: 185 },
    //       { date: '2027', price: 205 },
    //     ]
    //   },
    //   { 
    //     symbol: 'AMZN', 
    //     name: 'Amazon',
    //     correlation: 0.83,
    //     data: [
    //       { date: '2022', price: 115 },
    //       { date: '2023', price: 135 },
    //       { date: '2024', price: 155 },
    //       { date: '2025', price: 175 },
    //       { date: '2026', price: 195 },
    //       { date: '2027', price: 215 },
    //     ]
    //   },
    //   { 
    //     symbol: 'NVDA', 
    //     name: 'NVIDIA',
    //     correlation: 0.78,
    //     data: [
    //       { date: '2022', price: 125 },
    //       { date: '2023', price: 145 },
    //       { date: '2024', price: 165 },
    //       { date: '2025', price: 185 },
    //       { date: '2026', price: 205 },
    //       { date: '2027', price: 225 },
    //     ]
    //   },
    //   {
    //     symbol: 'META', 
    //     name: 'Meta Platforms',
    //     correlation: 0.72,
    //     data: [
    //       { date: '2022', price: 95 },
    //       { date: '2023', price: 115 },
    //       { date: '2024', price: 135 },
    //       { date: '2025', price: 155 },
    //       { date: '2026', price: 175 },
    //       { date: '2027', price: 195 },
    //     ]
    //   },
    // ];

    const [correlatedStocksData, setCorrelatedStocksData] = useState([{ticker: '', correlation: '', plot: '', name: ''}]);

    useEffect(() => {
      axios.get('http://localhost:3000/top5correlated', {params: { stockSymbol }})
      .then(response => {
        console.log(response.data)
        setCorrelatedStocksData(response.data);
        // console.log(correlatedStocksData);
      })
      .catch((error) => {
        console.error('Error fetching correlations:', error);
      });
    }, [stockSymbol]);
  
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8 relative z-0">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Chart Section */}
            <div className="lg:col-span-2 bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-3xl font-bold mb-6">{stockSymbol}</h2>
              <div className="mb-6">
                <PlotComponent stock={stockSymbol} selected_items={selectedLabels} />
              </div>
              <div className="flex flex-wrap gap-4">
                {options.map((option) => (
                  <div key={option.id}>
                    <input
                      type="checkbox"
                      id={`option-${option.id}`}
                      checked={selectedOptions.includes(option.id)} // Check if selected
                      onChange={() => handleCheckboxChange(option.id)}
                    />
                    <label htmlFor={`option-${option.id}`} style={{marginLeft: '8px'}}>{option.label}</label>
                  </div>
                ))}
              </div>
              
            </div>
  
            {/* Correlated Stocks Section */}
            <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">CORRELATED STOCKS</h2>
            <div className="h-[700px] overflow-y-auto pr-2">
              {correlatedStocksData.map((stock, index) => (
                <div key={index} className="mb-6 border-b pb-4 last:border-b-0">
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <h3 className="text-lg font-semibold">{stock.ticker}</h3>
                      <p className="text-sm text-gray-600">{stock.name || ''}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Correlation: {stock.correlation}
                      </span>
                    </div>
                  </div>
                  <div className="mt-2">
                    <img src={`data:image/png;base64,${stock.plot}`} />
                    {/* <LineChart width={300} height={120} data={stock.data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                      <YAxis domain={['dataMin - 10', 'dataMax + 10']} hide />
                      <Tooltip />
                      <Line type="monotone" dataKey="price" stroke="#4f46e5" strokeWidth={2} dot={false} />
                    </LineChart> */}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        </main>
      </div>
    );
  }

  export default Homepage