import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Predict from "./components/Predict.jsx";
import Train from "./components/Train.jsx";
import Upload from "./components/Upload.jsx";
import Visualize from "./components/Visualize.jsx";

// A placeholder for the default route, you can replace it with your actual content
const AnotherPage = () => <div className="p-4">This is Another Page</div>;

function App() {
  return (
    <Router>
      <div className="flex h-screen">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-gray-800 text-white p-4 h-full flex flex-col">
          <h1 className="text-xl font-bold mb-4">Dashboard</h1>
          <ul className="space-y-2">
            <li>
              <NavLink
                to="/predict"
                className={({ isActive }) => 
                  `block p-2 hover:bg-gray-700 rounded ${isActive ? 'bg-gray-700' : ''}`
                }
              >
                Prediction
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/upload"
                className={({ isActive }) => 
                  `block p-2 hover:bg-gray-700 rounded ${isActive ? 'bg-gray-700' : ''}`
                }
              >
                Upload Data & Preprocessing
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/train"
                className={({ isActive }) => 
                  `block p-2 hover:bg-gray-700 rounded ${isActive ? 'bg-gray-700' : ''}`
                }
              >
                Training Model & Postprocessing
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/visualize"
                className={({ isActive }) => 
                  `block p-2 hover:bg-gray-700 rounded ${isActive ? 'bg-gray-700' : ''}`
                }
              >
                Data Visualization
              </NavLink>
            </li>
          </ul>
        </nav>

        {/* Main Content */}
        <div className="flex-1 bg-gray-100 p-4 overflow-auto">
          <Routes>
            <Route path="/" element={<AnotherPage />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/train" element={<Train />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/visualize" element={<Visualize />} />

          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
