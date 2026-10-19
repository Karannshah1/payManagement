import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Target, TrendingUp, Plus } from 'lucide-react';

const Goals = () => {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newGoal, setNewGoal] = useState({ name: '', target_amount: '', target_date: '' });

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const response = await axios.get(`${API_BASE}/goals/api/goals`);
      setGoals(response.data);
    } catch (error) {
      console.error('API failed', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/goals/api/goals`, {
        name: newGoal.name,
        target_amount: parseFloat(newGoal.target_amount),
        target_date: newGoal.target_date
      });
      setNewGoal({ name: '', target_amount: '', target_date: '' });
      fetchGoals();
    } catch (error) {
      console.error('Error creating goal', error);
      alert('Failed to create goal');
    }
  };

  const handleContribute = async (id, name) => {
    const amountStr = prompt(`Enter amount to contribute to '${name}':`);
    if (!amountStr) return;
    const amount = parseFloat(amountStr);
    if (isNaN(amount) || amount <= 0) {
      alert("Please enter a valid amount.");
      return;
    }

    try {
      await axios.post(`http://localhost:5000/goals/api/goals/${id}/contribute`, {
        amount: amount
      });
      fetchGoals();
    } catch (error) {
      console.error('Error contributing', error);
      alert('Failed to contribute');
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center text-gray-900 dark:text-gray-100"><Target className="mr-2" /> Savings Goals</h1>
      
      {/* Create Goal Form */}
      <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center text-gray-900 dark:text-gray-100"><Plus className="mr-2" /> Create New Goal</h2>
        <form className="grid grid-cols-1 md:grid-cols-4 gap-4" onSubmit={handleCreateGoal}>
          <input 
            type="text" 
            placeholder="Goal Name (e.g., Vacation)" 
            value={newGoal.name}
            onChange={e => setNewGoal({...newGoal, name: e.target.value})}
            required
            className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          <input 
            type="number" 
            placeholder="Target Amount (?)" 
            value={newGoal.target_amount}
            onChange={e => setNewGoal({...newGoal, target_amount: e.target.value})}
            required
            className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          <input 
            type="date" 
            value={newGoal.target_date}
            onChange={e => setNewGoal({...newGoal, target_date: e.target.value})}
            required
            className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          />
          <button type="submit" className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 transition font-medium">Create Goal</button>
        </form>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? <p className="text-gray-900 dark:text-gray-100">Loading...</p> : goals.map((goal) => {
          const current = goal.current_amount || 0;
          const target = goal.target_amount || 1;
          const progress = Math.min((current / target) * 100, 100).toFixed(1);
          return (
            <div key={goal.id} className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md border border-gray-100 dark:border-gray-600 flex flex-col">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{goal.name}</h3>
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">{progress}%</span>
              </div>
              
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-4">
                <div className="bg-blue-600 h-4 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
              </div>
              
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-6 flex-grow">
                <span>Current: ?{current.toLocaleString()}</span>
                <span>Target: ?{target.toLocaleString()}</span>
              </div>
              
              <button 
                onClick={() => handleContribute(goal.id, goal.name)}
                className="w-full bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-100 p-2 rounded hover:bg-blue-50 dark:hover:bg-gray-600 hover:text-blue-600 flex items-center justify-center font-medium transition-colors"
              >
                <TrendingUp className="mr-2 h-4 w-4" /> Contribute
              </button>
            </div>
          );
        })}
        {goals.length === 0 && !loading && (
          <div className="col-span-full text-center text-gray-500 dark:text-gray-400 py-8">
            No savings goals found. Create one above!
          </div>
        )}
      </div>
    </div>
  );
};

export default Goals;
