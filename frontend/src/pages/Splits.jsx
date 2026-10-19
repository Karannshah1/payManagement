import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Plus, DollarSign } from 'lucide-react';

const Splits = () => {
  const [splits, setSplits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSplits();
  }, []);

  const fetchSplits = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/splits/api/splits`);
      setSplits(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch splits data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4">Loading splits...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center"><Users className="mr-2" /> Split Groups</h1>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md border border-gray-100">
           <h2 className="text-xl font-semibold mb-4">Create New Split</h2>
           <form className="space-y-4">
               <div>
                   <label className="block text-sm font-medium text-gray-700">Group Name</label>
                   <input type="text" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border" />
               </div>
               <button type="button" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                   <Plus className="mr-2 h-4 w-4" /> Create Group
               </button>
           </form>
        </div>
        <div>
            <h2 className="text-xl font-semibold mb-4">Your Groups</h2>
            {splits.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400">No split groups found.</p>
            ) : (
                <div className="space-y-4">
                    {splits.map(split => (
                        <div key={split.id} className="bg-white dark:bg-gray-800 dark:border-gray-700 p-4 rounded-lg shadow border border-gray-100">
                            <h3 className="font-medium text-lg">{split.name}</h3>
                            <div className="mt-2 text-sm text-gray-600">
                                {split.members?.map(m => (
                                    <div key={m.id} className="flex justify-between mt-1">
                                        <span>{m.name}</span>
                                        <span className={m.owes > 0 ? "text-red-500" : "text-green-500"}>
                                            {m.owes > 0 ? `Owes ₹${m.owes}` : `Paid ₹${Math.abs(m.owes)}`}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default Splits;
