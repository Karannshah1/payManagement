import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar, Repeat, CreditCard } from 'lucide-react';

const Subscriptions = () => {
    const [subscriptions, setSubscriptions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchSubscriptions();
    }, []);

    const fetchSubscriptions = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_BASE}/subscriptions/api/subscriptions`);
            setSubscriptions(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch subscriptions');
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-4">Loading subscriptions...</div>;
    if (error) return <div className="p-4 text-red-500">{error}</div>;

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6 flex items-center"><Repeat className="mr-2" /> Subscriptions</h1>
            <div className="bg-white dark:bg-gray-800 dark:border-gray-700 rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50 dark:bg-gray-900">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Name</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Amount</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Billing Cycle</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Next Renewal</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 dark:border-gray-700 divide-y divide-gray-200">
                        {subscriptions.map(sub => (
                            <tr key={sub.id}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    <div className="flex items-center">
                                        <CreditCard className="h-5 w-5 text-gray-400 mr-2" />
                                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{sub.name}</div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                    ₹{sub.amount}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                    {sub.cycle}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                                    <div className="flex items-center">
                                        <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                                        {sub.nextRenewalDate}
                                    </div>
                                </td>
                            </tr>
                        ))}
                        {subscriptions.length === 0 && (
                            <tr>
                                <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                                    No subscriptions found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Subscriptions;
