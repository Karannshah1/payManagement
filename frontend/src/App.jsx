import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Expenses from './pages/Expenses';
import Budgets from './pages/Budgets';
import Income from './pages/Income';
import Accounts from './pages/Accounts';
import Goals from './pages/Goals';
import Emi from './pages/Emi';
import Splits from './pages/Splits';
import Subscriptions from './pages/Subscriptions';
import Reminders from './pages/Reminders';
import Analytics from './pages/Analytics';
import SmartImport from './pages/SmartImport';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/income" element={<Income />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/budgets" element={<Budgets />} />
          <Route path="/goals" element={<Goals />} />
          <Route path="/emi" element={<Emi />} />
          <Route path="/splits" element={<Splits />} />
          <Route path="/subscriptions" element={<Subscriptions />} />
          <Route path="/reminders" element={<Reminders />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/import" element={<SmartImport />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
