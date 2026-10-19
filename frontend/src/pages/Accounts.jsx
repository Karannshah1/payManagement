import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CreditCard, ArrowRightLeft, Plus } from 'lucide-react';

const Accounts = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [newAccount, setNewAccount] = useState({ name: '', type: 'bank', balance: '' });
  const [transferData, setTransferData] = useState({ from_account_id: '', to_account_id: '', amount: '' });

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/accounts/api/accounts`);
      setAccounts(response.data);
    } catch (error) {
      console.error('API failed', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/accounts/api/accounts`, {
        name: newAccount.name,
        type: newAccount.type,
        balance: parseFloat(newAccount.balance) || 0
      });
      setNewAccount({ name: '', type: 'bank', balance: '' });
      fetchAccounts(); // Refresh
    } catch (error) {
      console.error('Error creating account', error);
      alert('Failed to create account');
    }
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/accounts/api/accounts/transfer`, {
        from_account_id: parseInt(transferData.from_account_id),
        to_account_id: parseInt(transferData.to_account_id),
        amount: parseFloat(transferData.amount)
      });
      setTransferData({ from_account_id: '', to_account_id: '', amount: '' });
      fetchAccounts(); // Refresh balances
    } catch (error) {
      console.error('Error transferring', error);
      alert('Failed to transfer money');
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center text-gray-900 dark:text-gray-100"><CreditCard className="mr-2" /> Accounts</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {loading ? <p className="text-gray-900 dark:text-gray-100">Loading...</p> : accounts.map((acc) => (
          <div key={acc.id} className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md border-t-4 border-blue-500">
            <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-100">{acc.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{acc.type || 'Account'}</p>
            <p className={`text-2xl font-bold ${acc.balance < 0 ? 'text-red-500' : 'text-green-500'}`}>
              ?{acc.balance.toLocaleString()}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 flex items-center text-gray-900 dark:text-gray-100"><Plus className="mr-2" /> Add Account</h2>
          <form className="space-y-4" onSubmit={handleCreateAccount}>
            <input 
              type="text" 
              placeholder="Account Name" 
              value={newAccount.name}
              onChange={(e) => setNewAccount({...newAccount, name: e.target.value})}
              required
              className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
            />
            <select 
              value={newAccount.type}
              onChange={(e) => setNewAccount({...newAccount, type: e.target.value})}
              className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="bank">Bank Account</option>
              <option value="cash">Cash</option>
              <option value="credit_card">Credit Card</option>
              <option value="upi_wallet">UPI Wallet</option>
            </select>
            <input 
              type="number" 
              placeholder="Initial Balance (?)" 
              value={newAccount.balance}
              onChange={(e) => setNewAccount({...newAccount, balance: e.target.value})}
              className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
            />
            <button type="submit" className="bg-blue-600 text-white w-full p-2 rounded hover:bg-blue-700 transition">Create Account</button>
          </form>
        </div>

        <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 flex items-center text-gray-900 dark:text-gray-100"><ArrowRightLeft className="mr-2" /> Transfer Money</h2>
          <form className="space-y-4" onSubmit={handleTransfer}>
            <select 
              value={transferData.from_account_id}
              onChange={(e) => setTransferData({...transferData, from_account_id: e.target.value})}
              required
              className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">From Account...</option>
              {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
            <select 
              value={transferData.to_account_id}
              onChange={(e) => setTransferData({...transferData, to_account_id: e.target.value})}
              required
              className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">To Account...</option>
              {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
            <input 
              type="number" 
              placeholder="Amount (?)" 
              value={transferData.amount}
              onChange={(e) => setTransferData({...transferData, amount: e.target.value})}
              required
              className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" 
            />
            <button type="submit" className="bg-green-600 text-white w-full p-2 rounded hover:bg-green-700 transition">Transfer Funds</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Accounts;
