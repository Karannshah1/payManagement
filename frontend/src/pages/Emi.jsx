import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar, CheckCircle, Plus, Wallet } from 'lucide-react';

const Emi = () => {
  const [emis, setEmis] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    amount: '',
    total_months: '12',
    account_id: ''
  });

  useEffect(() => {
    fetchEmis();
    fetchAccounts();
  }, []);

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

  const fetchEmis = async () => {
    try {
      const response = await axios.get(`${API_BASE}/emi/api/emi`);
      setEmis(response.data || []);
    } catch (error) {
      console.error('API failed', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePay = async (id) => {
    try {
      await axios.post(`${API_BASE}/emi/api/emi/${id}/pay`);
      fetchEmis();
      fetchAccounts();
    } catch (error) {
      console.error('Error paying EMI', error);
      alert('Failed to process payment: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/emi/api/emi`, {
        name: formData.name,
        amount: parseFloat(formData.amount),
        total_months: parseInt(formData.total_months),
        account_id: formData.account_id
      });
      setShowForm(false);
      setFormData({
        name: '',
        amount: '',
        total_months: '12',
        account_id: accounts.length > 0 ? accounts[0].id : ''
      });
      fetchEmis();
    } catch (error) {
      console.error('Error adding EMI', error);
      alert('Failed to create EMI: ' + (error.response?.data?.error || error.message));
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold flex items-center text-gray-800 dark:text-gray-100">
          <Calendar className="mr-2 text-indigo-600" /> EMI Management
        </h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-indigo-700 transition shadow-sm font-medium"
        >
          <Plus size={20} /> Add EMI
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 p-6 rounded-xl shadow-md mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Loan / EMI Name</label>
            <input
              type="text"
              placeholder="e.g. Home Loan, Car Loan"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Monthly Amount (₹)</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Total Tenure (Months)</label>
            <input
              type="number"
              placeholder="e.g. 12, 24, 60"
              value={formData.total_months}
              onChange={(e) => setFormData({ ...formData, total_months: e.target.value })}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Deduct From Account</label>
            <select
              value={formData.account_id}
              onChange={(e) => setFormData({ ...formData, account_id: e.target.value })}
              className="w-full border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500"
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
              Save EMI
            </button>
          </div>
        </form>
      )}
      
      <div className="space-y-4">
        {loading ? (
          <p className="text-gray-500">Loading EMIs...</p>
        ) : emis.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow text-center text-gray-500 dark:text-gray-400">
            No active EMIs tracked. Click <strong>Add EMI</strong> to track your loans.
          </div>
        ) : (
          emis.map((emi) => {
            const completed = emi.completed_months ?? emi.completedMonths ?? 0;
            const total = emi.total_months ?? emi.totalTenure ?? 1;
            const remainingMonths = Math.max(0, total - completed);
            const progress = ((completed / total) * 100).toFixed(1);
            const amount = emi.amount ?? emi.emiAmount ?? 0;
            
            return (
              <div key={emi.id} className="bg-white dark:bg-gray-800 dark:border dark:border-gray-700 p-6 rounded-xl shadow-md flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex-1 w-full">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">{emi.name}</h3>
                    <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-1">
                      <Wallet size={15} /> {emi.account_name || 'Bank Account'}
                    </span>
                  </div>
                  <p className="text-indigo-600 dark:text-indigo-400 font-bold text-lg mb-2">₹{amount.toLocaleString('en-IN')} / month</p>
                  
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2 space-x-4">
                    <span>Tenure: {total} months</span>
                    <span>Completed: {completed} months</span>
                    <span>Remaining: {remainingMonths} months</span>
                  </div>
                  
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 max-w-md overflow-hidden">
                    <div className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
                  </div>
                </div>
                
                <div>
                  <button 
                    onClick={() => handlePay(emi.id)}
                    disabled={remainingMonths === 0}
                    className={`px-5 py-2.5 rounded-lg font-medium flex items-center transition shadow-sm ${
                      remainingMonths === 0 
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed' 
                      : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                  >
                    <CheckCircle className="mr-2 h-5 w-5" />
                    {remainingMonths === 0 ? 'Completed' : 'Pay EMI'}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Emi;
