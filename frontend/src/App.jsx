import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Suppliers from './pages/Suppliers';
import SupplierDetail from './pages/SupplierDetail';
import Events from './pages/Events';
import Recovery from './pages/Recovery';
import Simulate from './pages/Simulate';
import N8nStatus from './pages/N8nStatus';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="suppliers" element={<Suppliers />} />
          <Route path="suppliers/:id" element={<SupplierDetail />} />
          <Route path="events" element={<Events />} />
          <Route path="recovery" element={<Recovery />} />
          <Route path="simulate" element={<Simulate />} />
          <Route path="n8n" element={<N8nStatus />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
