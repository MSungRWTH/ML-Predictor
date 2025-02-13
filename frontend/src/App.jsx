import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ModelManager from "./components/home.jsx";
import ModelTraining from "./components/trainmodel.jsx";

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
              <Link to="/" className="block p-2 hover:bg-gray-700 rounded">Home</Link>
            </li>
            <li>
              <Link to="/trainmodel" className="block p-2 hover:bg-gray-700 rounded">Training</Link>
            </li>
          </ul>
        </nav>

        {/* Main Content */}
        <div className="flex-1 bg-gray-100 p-4 overflow-auto">
          <Routes>
            <Route path="/" element={<ModelManager />} />
            <Route path="/trainmodel" element={<ModelTraining />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;