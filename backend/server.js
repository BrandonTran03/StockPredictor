import express from 'express';
import cors from 'cors';  // Import cors package
import axios from 'axios';

const app = express();
const port = 3000;

// Enable CORS for all domains (or restrict to specific domains)
app.use(cors());  // This allows requests from any origin
// If you want to restrict CORS to a specific domain, use:
// app.use(cors({ origin: 'http://localhost:5173' }));

app.get('/plot', async (req, res) => {
  const { stock, selected_items } = req.query;

  try {
    let params_string = JSON.stringify({
      stock: stock,
      selected_items: selected_items
    });

    // Making a request to the Flask server
    const response = await axios.get('http://localhost:5000/plot', {
      params: {
        params: params_string
      }
    });
    const plotData = response.data.plot;  // Base64 string of the plot image

    // Return the Base64 string back to the React app
    res.json({ plot: plotData });
  } catch (error) {
    console.error('Error fetching plot:', error);
    res.status(500).send('Error fetching plot');
  }
});

app.get('/tickers', async (req, res) => {
  try {
    // Making a request to the Flask server
    const response = await axios.get('http://localhost:5000/tickers');
    const tickers = response.data.tickers;

    res.json({ tickers: tickers });
  } catch (error) {
    console.error('Error fetching:', error);
    res.status(500).send('Error fetching');
  }
});

app.get('/topcorrelated', async (req, res) => {
  try {
    // Making a request to the Flask server
    const response = await axios.get('http://localhost:5000/topcorrelated');
    
    const correlated_stocks = response.data;

    res.json(correlated_stocks);
  } catch (error) {
    console.error('Error fetching stocks:', error);
    res.status(500).send('Error fetching stocks');
  }
});

app.get('/top5correlated', async (req, res) => {
  const { stockSymbol } = req.query;
  console.log(stockSymbol);

  try {
    let params_string = JSON.stringify({
      stock: stockSymbol
    });

    // Making a request to the Flask server
    const response = await axios.get('http://localhost:5000/top5correlated', {
      params: {
        params: params_string
      }
    });
    
    const correlated_stocks = response.data;

    res.json(correlated_stocks);
  } catch (error) {
    console.error('Error fetching stocks:', error);
    res.status(500).send('Error fetching stocks');
  }
});

app.get('/topStocks', async (req, res) => {
  try {
    // Making a request to the Flask server
    const response = await axios.get('http://localhost:5000/topStocks');
    
    const top_stocks = response.data;

    res.json(top_stocks);
  } catch (error) {
    console.error('Error fetching stocks:', error);
    res.status(500).send('Error fetching stocks');
  }
});

app.get('/topStocksPredicted', async (req, res) => {
  try {
    // Making a request to the Flask server
    const response = await axios.get('http://localhost:5000/topStocksPredicted');
    
    const top_stocks = response.data;

    res.json(top_stocks);
  } catch (error) {
    console.error('Error fetching stocks:', error);
    res.status(500).send('Error fetching stocks');
  }
});

app.listen(port, () => {
  console.log(`Node.js server is running on http://localhost:${port}`);
});