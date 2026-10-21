import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus } from 'lucide-react';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    category_id: '',
    limit: ''
  });

  const fetchBudgets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/budgets/api/budgets`);
      setBudgets(response.data || []);
    } catch (error) {
      console.error('Error fetching budgets:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const res = await axios.get(`${API_BASE}/categories/api/categories`);
      setCategories(res.data || []);
      if (res.data && res.data.length > 0 && !formData.category_id) {
        setFormData(prev => ({
          ...prev,
          category_id: res.data[0].id,
          category: res.data[0].name
        }));
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  useEffect(() => {
    fetchBudgets();
    fetchCategories();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'category_id') {
      const selected = categories.find(c => c.id === parseInt(value));
      setFormData({
        ...formData,
        category_id: value,
        category: selected ? selected.name : ''
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/budgets/api/budgets`, {
        category_id: formData.category_id,
        category: formData.category,
        limit: parseFloat(formData.limit)
      });
      setShowForm(false);
      setFormData({
        category: categories.length > 0 ? categories[0].name : '',
        category_id: categories.length > 0 ? categories[0].id : '',
        limit: ''
      });
      fetchBudgets();
    } catch (error) {
      console.error('Error creating budget:', error);
      alert('Failed to save budget: ' + (error.response?.data?.error || error.message));
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
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700 transition shadow-sm font-medium"
        >
          <Plus size={20} />
          Set Budget
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 p-6 rounded-xl shadow-md mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleInputChange}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="">Select Category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Monthly Budget Limit (₹)</label>
            <input
              type="number"
              step="0.01"
              name="limit"
              placeholder="e.g. 10000"
              value={formData.limit}
              onChange={handleInputChange}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div className="md:col-span-2 flex justify-end gap-3 mt-2">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-medium shadow-sm"
            >
              Save Budget
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {budgets.map((budget) => {
          const actual = budget.actual_spend || 0;
          const limit = budget.amount || budget.limit || 0;
          const percentage = calculatePercentage(actual, limit);
          
          return (
            <div key={budget.id || budget.category_name} className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 p-5 rounded-xl shadow-md">
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">{budget.category_name || budget.category}</h3>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">₹{actual.toLocaleString('en-IN')} / ₹{limit.toLocaleString('en-IN')}</span>
              </div>
              
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-2 overflow-hidden">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(percentage)}`} 
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>{percentage.toFixed(0)}% used</span>
                <span>{limit > actual ? `₹${(limit - actual).toLocaleString('en-IN')} left` : 'Over budget!'}</span>
              </div>
            </div>
          );
        })}
        {budgets.length === 0 && (
          <div className="col-span-full py-12 text-center text-gray-500 dark:text-gray-400">
            No budgets configured yet. Click <strong>Set Budget</strong> to define category spending limits.
          </div>
        )}
      </div>
    </div>
  );
};

export default Budgets;
