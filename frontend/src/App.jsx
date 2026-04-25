import { useEffect, useState } from 'react';
import { fetchData } from './api/endpoints';

function App() {
  const [items, setItems] = useState([]);
  const [isConnected, setIsConnected] = useState(false); // New state

  //sample changes commit
 useEffect(() => {
    fetchData()
      .then((data) => {
        if (data) {
          setItems(data);
          setIsConnected(true);
        }
      })
      .catch((err) => {
        
        console.log("Server is down");
        setIsConnected(false);
        setItems([]);
      });
  }, []);

  return (
    <div>
      <h1>Backend Status: {isConnected ? "TRUE" : "FALSE"}</h1>
      
      <hr />
      
      <h2>Backend Data:</h2>
      {items.length > 0 ? (
        items.map(item => <div key={item.id}>{item.name}</div>)
      ) : (
        <p>No data available.</p>
      )}
    </div>
  );
}

export default App;