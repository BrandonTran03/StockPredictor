import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface PlotComponentProps {
  stock: string;
  selected_items: string[];
}

const PlotComponent: React.FC<PlotComponentProps> = ({ stock, selected_items }) => {
  const [plot, setPlot] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Fetch the plot from the Node.js server
    axios.get('http://localhost:3000/plot', {params: {stock, selected_items}})  // Node.js server endpoint
      .then((response) => {
        // console.log(response.data.plot);
        setPlot(response.data.plot);  // Base64 encoded plot
        setLoading(false);  // Stop loading once the plot is fetched
      })
      .catch((error) => {
        console.error('Error fetching plot:', error);
        setLoading(false);  // Stop loading on error
      });
  }, [stock, selected_items]);

  return (
    <div>
      {/* <h3>Matplotlib Plot</h3> */}
      {loading ? (
        <p>Loading plot...</p>
      ) : (
        plot.length == 0 ? (
          <p>No data was found...</p>
        ) : (
        <img src={`data:image/png;base64,${plot}`} />
      ))}
    </div>
  );
};

export default PlotComponent;