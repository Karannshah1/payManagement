import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, IndianRupee, Wallet } from 'lucide-react';

const Income = () => {
  const [incomes, setIncomes] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    source: '',
    amount: '',
    account_id: ''
  });

  const fetchAccounts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/accounts/api/accounts`);
      setAccounts(res.data || []);
      if (res.data && res.data.length > 0 && !formData.account_id) {
        setFormData(prev => ({ ...prev, account_id: res.data[0].id }));
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const fetchIncomes = async () => {
    try {
      const response = await axios.get(`${API_BASE}/income/api/income`);
      setIncomes(response.data.income || []);
    } catch (error) {
      console.error('API failed', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncomes();
    fetchAccounts();
  }, []);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/income/api/income`, {
        ...formData,
        amount: parseFloat(formData.amount)
      });
      fetchIncomes();
      fetchAccounts();
      setFormData({
        date: new Date().toISOString().split('T')[0],
        source: '',
        amount: '',
        account_id: accounts.length > 0 ? accounts[0].id : ''
      });
    } catch (error) {
      console.error('Error adding income', error);
      alert('Failed to save income: ' + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center text-gray-800 dark:text-gray-100">
        <IndianRupee className="mr-2 text-green-600" /> Income Management
      </h1>
      
      <div className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 p-6 rounded-xl shadow-md mb-8">
        <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-gray-200">Add New Income</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Date</label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleInputChange}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Source / Payer</label>
            <input
              type="text"
              name="source"
              placeholder="e.g. Salary, Freelance, Dividend"
              value={formData.source}
              onChange={handleInputChange}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Amount (₹)</label>
            <input
              type="number"
              step="0.01"
              name="amount"
              placeholder="0.00"
              value={formData.amount}
              onChange={handleInputChange}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-500 mb-1">Deposit To Account</label>
            <select
              name="account_id"
              value={formData.account_id}
              onChange={handleInputChange}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-green-500"
              required
            >
              <option value="">Select Account</option>
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} (₹{a.balance?.toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            className="bg-green-600 text-white p-2.5 rounded-lg hover:bg-green-700 transition flex items-center justify-center font-medium md:col-span-4 shadow-sm"
          >
            <Plus className="mr-2" size={18} /> Add Income
          </button>
        </form>
      </div>

      <div className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 rounded-xl shadow-md overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-900 border-b dark:border-gray-700">
              <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Date</th>
              <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Source</th>
              <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Amount</th>
              <th className="p-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Account</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr><td colSpan="4" className="p-6 text-center text-gray-500">Loading income records...</td></tr>
            ) : incomes.length === 0 ? (
              <tr><td colSpan="4" className="p-8 text-center text-gray-500">No income entries found.</td></tr>
            ) : (
              incomes.map((income) => (
                <tr key={income.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition">
                  <td className="p-4 text-sm text-gray-700 dark:text-gray-300">{income.date}</td>
                  <td className="p-4 text-sm font-medium text-gray-900 dark:text-gray-100">{income.source}</td>
                  <td className="p-4 text-sm font-semibold text-green-600 dark:text-green-400">+₹{parseFloat(income.amount).toLocaleString('en-IN')}</td>
                  <td className="p-4 text-sm text-gray-700 dark:text-gray-300">
                    <span className="inline-flex items-center gap-1.5">
                      <Wallet size={15} className="text-gray-400" />
                      {income.account_name || income.account || 'Default'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Income;
