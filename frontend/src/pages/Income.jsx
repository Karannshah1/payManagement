import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, IndianRupee } from 'lucide-react';

const Income = () => {
  const [incomes, setIncomes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ date: '', source: '', amount: '', account: '' });

  useEffect(() => {
    fetchIncomes();
  }, []);

  const fetchIncomes = async () => {
    try {
      const response = await axios.get(`${API_BASE}/income/api/income`);
      setIncomes(response.data.income || []);
    } catch (error) {
      console.error('API failed, using dummy data', error);
      setIncomes([
        { id: 1, date: '2026-10-01', source: 'Salary', amount: 50000, account: 'HDFC Bank' },
        { id: 2, date: '2026-10-05', source: 'Freelance', amount: 15000, account: 'SBI' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/income/api/income`, formData);
      fetchIncomes();
      setFormData({ date: '', source: '', amount: '', account: '' });
    } catch (error) {
      console.error('Error adding income', error);
      // fallback add to UI
      setIncomes([...incomes, { ...formData, id: Date.now() }]);
      setFormData({ date: '', source: '', amount: '', account: '' });
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center"><IndianRupee className="mr-2" /> Income Management</h1>
      
      <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4">Add New Income</h2>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input type="date" name="date" value={formData.date} onChange={handleInputChange} className="border dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 rounded" required />
          <input type="text" name="source" placeholder="Source" value={formData.source} onChange={handleInputChange} className="border dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 rounded" required />
          <input type="number" name="amount" placeholder="Amount (₹)" value={formData.amount} onChange={handleInputChange} className="border dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 rounded" required />
          <input type="text" name="account" placeholder="Account" value={formData.account} onChange={handleInputChange} className="border dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 rounded" required />
          <button type="submit" className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 flex items-center justify-center md:col-span-4">
            <Plus className="mr-2" /> Add Income
          </button>
        </form>
      </div>

      <div className="bg-white dark:bg-gray-800 dark:border-gray-700 rounded-lg shadow-md overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-100 dark:bg-gray-800">
              <th className="p-4 border-b text-gray-800 dark:text-gray-200">Date</th>
              <th className="p-4 border-b text-gray-800 dark:text-gray-200">Source</th>
              <th className="p-4 border-b text-gray-800 dark:text-gray-200">Amount</th>
              <th className="p-4 border-b text-gray-800 dark:text-gray-200">Account</th>
            </tr>
          </thead>
          <tbody>
            {loading ? <tr><td colSpan="4" className="p-4 text-center">Loading...</td></tr> : 
             incomes.map((income) => (
              <tr key={income.id} className="hover:bg-gray-50 dark:bg-gray-900">
                <td className="p-4 border-b text-gray-700 dark:text-gray-300">{income.date}</td>
                <td className="p-4 border-b text-gray-700 dark:text-gray-300">{income.source}</td>
                <td className="p-4 border-b text-gray-700 dark:text-gray-300">₹{income.amount}</td>
                <td className="p-4 border-b text-gray-700 dark:text-gray-300">{income.account}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Income;


