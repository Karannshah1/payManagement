import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus } from 'lucide-react';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    limit: ''
  });

  const fetchBudgets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/budgets/api/budgets`);
      setBudgets(response.data);
    } catch (error) {
      console.error('Error fetching budgets:', error);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/budgets/api/budgets`, {
        category: formData.category,
        limit: parseFloat(formData.limit)
      });
      setShowForm(false);
      setFormData({ category: '', limit: '' });
      fetchBudgets();
    } catch (error) {
      console.error('Error creating budget:', error);
    }
  };

  const calculatePercentage = (actual, limit) => {
    if (!limit || limit === 0) return 0;
    const percentage = (actual / limit) * 100;
    return percentage > 100 ? 100 : percentage;
  };

  const getProgressColor = (percentage) => {
    if (percentage < 70) return 'bg-green-500';
    if (percentage < 90) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100">Budgets</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-blue-700 transition"
        >
          <Plus size={20} />
          Set Budget
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <input type="text" name="category" value={formData.category} onChange={handleInputChange} className="w-full border p-2 rounded" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Budget Limit (₹)</label>
            <input type="number" name="limit" value={formData.limit} onChange={handleInputChange} className="w-full border p-2 rounded" required />
          </div>
          <div className="md:col-span-2 flex justify-end gap-2 mt-2">
            <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600 bg-gray-100 dark:bg-gray-800 rounded hover:bg-gray-200">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save Budget</button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {budgets.map((budget) => {
          const actual = budget.actual_spend || 0;
          const limit = budget.limit || 0;
          const percentage = calculatePercentage(actual, limit);
          
          return (
            <div key={budget.id || budget.category} className="bg-white dark:bg-gray-800 dark:border-gray-700 p-5 rounded-lg shadow">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">{budget.category}</h3>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">₹{actual} / ₹{limit}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2 mt-4">
                <div 
                  className={`h-2.5 rounded-full ${getProgressColor(percentage)}`} 
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {percentage.toFixed(1)}% used
              </p>
            </div>
          );
        })}
        
        {budgets.length === 0 && (
          <div className="col-span-full text-center text-gray-500 dark:text-gray-400 py-10 bg-white dark:bg-gray-800 dark:border-gray-700 rounded-lg shadow">
            No budgets set yet. Click "Set Budget" to create one.
          </div>
        )}
      </div>
    </div>
  );
};

export default Budgets;
