import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bell, CheckCircle } from 'lucide-react';

const Reminders = () => {
    const [reminders, setReminders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchReminders();
    }, []);

    const fetchReminders = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_BASE}/reminders/api/reminders`);
            setReminders(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch reminders');
        } finally {
            setLoading(false);
        }
    };

    const markCompleted = async (id) => {
        try {
            await axios.put(`${API_BASE}/reminders/api/reminders/${id}/complete`);
            fetchReminders();
        } catch (err) {
            alert('Failed to mark as completed');
        }
    };

    if (loading) return <div className="p-4">Loading reminders...</div>;
    if (error) return <div className="p-4 text-red-500">{error}</div>;

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6 flex items-center"><Bell className="mr-2" /> Reminders</h1>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {reminders.map(reminder => (
                    <div key={reminder.id} className={`p-4 rounded-lg shadow border ${reminder.isCompleted ? 'bg-gray-50 dark:bg-gray-900 border-gray-200' : 'bg-white dark:bg-gray-800 dark:border-gray-700 border-blue-200'}`}>
                        <div className="flex justify-between items-start mb-2">
                            <h3 className={`font-medium ${reminder.isCompleted ? 'text-gray-500 dark:text-gray-400 line-through' : 'text-gray-900 dark:text-gray-100'}`}>
                                {reminder.title}
                            </h3>
                            {!reminder.isCompleted && (
                                <button onClick={() => markCompleted(reminder.id)} className="text-green-600 hover:text-green-700" title="Mark Completed">
                                    <CheckCircle className="h-5 w-5" />
                                </button>
                            )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">Due: {reminder.dueDate}</p>
                        <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">₹{reminder.amount}</p>
                    </div>
                ))}
                {reminders.length === 0 && (
                    <div className="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">
                        No reminders found.
                    </div>
                )}
            </div>
        </div>
    );
};

export default Reminders;
