import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Homepage from './pages/Homepage';  // Component for stock details
import TeamPage from './pages/TeamPage';
import TopCorrelatedStocks from './pages/TopCorrelatedStocks'
import TopStocks from './pages/TopStocks';
import TopStocksPredicted from './pages/TopStocksPredicted';

function App() {
  return (
    <Router> {/* Router wraps your entire app */}

      <Header />

      <Routes>
        <Route path="/" element={<Homepage />} />  {/* Home route */}
        <Route path="/stock/:stockSymbol" element={<Homepage />} /> {/* Dynamic stock detail route */}
        <Route path="/team" element={<TeamPage />} /> {/* New route for About page */}
        <Route path="/topCorrelated" element={<TopCorrelatedStocks />} /> {/* New route for About page */}
        <Route path="/topStocks" element={<TopStocks />} /> {/* New route for About page */}
        <Route path="/topStocksPredicted" element={<TopStocksPredicted />} /> {/* New route for About page */}
      </Routes>
    </Router>
  );
}

export default App;