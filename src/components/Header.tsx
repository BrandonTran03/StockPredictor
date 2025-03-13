import { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import StockSearch from '../components/StockSearch';

function Header() {
    const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
    const navigate = useNavigate(); // Initialize useNavigate
  
    const toggleDropdown = (menu: string) => {
      setActiveDropdown(activeDropdown === menu ? null : menu);
    };

    // Navigate to a specific page when a menu item is clicked
    const handleNavigation = (path: string) => {
        setActiveDropdown('');
        navigate(path); // Navigate to the path
    };

    return (
        <div>
            <header className="bg-white shadow-sm relative z-20">
            <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold">Stock Predictor</h1>
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                </div>
                <div className="relative">
                <div className="relative">
                    {/* <input
                    type="text"
                    placeholder="Search Stock"
                    className="w-64 pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    /> */}
                    <StockSearch />
                    <svg
                    className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    >
                    <path
                        fillRule="evenodd"
                        d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
                        clipRule="evenodd"
                    />
                    </svg>
                </div>
                </div>
            </div>
            </header>

            {/* Navigation */}
            <nav className="border-b border-gray-200 relative z-10">
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex space-x-8">
                {/* Top 5 Stocks Dropdown */}
                <div className="relative h-14">
                    <button
                    onClick={() => toggleDropdown('top5')}
                    className="h-full px-3 text-gray-700 hover:text-gray-900 hover:border-b-2 hover:border-gray-900 flex items-center"
                    >
                    Top 5 stocks
                    <svg
                        className={`ml-2 h-5 w-5 transform ${
                        activeDropdown === 'top5' ? 'rotate-180' : ''
                        }`}
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                        />
                    </svg>
                    </button>
                    {activeDropdown === 'top5' && (
                    <div className="absolute left-0 top-full mt-0 w-48 py-2 bg-white rounded-md shadow-lg z-50">
                        <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100" onClick={(e) => {e.preventDefault(); handleNavigation('/topStocks')}}>Current</a>
                        <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100" onClick={(e) => {e.preventDefault(); handleNavigation('/topStocksPredicted')}}>Predicted</a>
                    </div>
                    )}
                </div>

                {/* Correlated Stocks Dropdown */}
                <div className="relative h-14">
                    <button
                    onClick={() => toggleDropdown('correlated')}
                    className="h-full px-3 text-gray-700 hover:text-gray-900 hover:border-b-2 hover:border-gray-900 flex items-center"
                    >
                    Correlated stocks
                    <svg
                        className={`ml-2 h-5 w-5 transform ${
                        activeDropdown === 'correlated' ? 'rotate-180' : ''
                        }`}
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                        />
                    </svg>
                    </button>
                    {activeDropdown === 'correlated' && (
                    <div className="absolute left-0 top-full mt-0 w-48 py-2 bg-white rounded-md shadow-lg z-50">
                        <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100" onClick={(e) => {e.preventDefault(); handleNavigation('/topCorrelated')}}>High Correlation</a>
                        {/* <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100">Medium Correlation</a>
                        <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100">Low Correlation</a> */}
                    </div>
                    )}
                </div>

                {/* About Us Dropdown */}
                <div className="relative h-14">
                    <button
                    onClick={() => toggleDropdown('about')}
                    className="h-full px-3 text-gray-700 hover:text-gray-900 hover:border-b-2 hover:border-gray-900 flex items-center"
                    >
                    About us
                    <svg
                        className={`ml-2 h-5 w-5 transform ${
                        activeDropdown === 'about' ? 'rotate-180' : ''
                        }`}
                        viewBox="0 0 20 20"
                        fill="currentColor"
                    >
                        <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                        />
                    </svg>
                    </button>
                    {activeDropdown === 'about' && (
                    <div className="absolute left-0 top-full mt-0 w-48 py-2 bg-white rounded-md shadow-lg z-50">
                        <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100" onClick={(e) => {e.preventDefault(); handleNavigation('/team')}}>Our Team</a>
                        {/* <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100">Contact</a>
                        <a href="#" className="block px-4 py-2 text-gray-800 hover:bg-gray-100">FAQ</a> */}
                    </div>
                    )}
                </div>
                </div>
            </div>
            </nav>
        </div>
    );
}

export default Header