import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Settings as SettingsIcon, Save } from 'lucide-react';

const Settings = () => {
    const [settings, setSettings] = useState({
        currencySymbol: '₹',
        fiscalYearStart: '04-01',
        defaultAccountId: ''
    });
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [settingsRes, accountsRes] = await Promise.all([
                axios.get(`${API_BASE}/settings/api/settings`).catch(() => ({ data: {} })),
                axios.get(`${API_BASE}/accounts/api/accounts`).catch(() => ({ data: [] }))
            ]);
            setSettings(prev => ({...prev, ...settingsRes.data}));
            setAccounts(accountsRes.data);
            setError(null);
        } catch (err) {
            setError('Failed to load settings data');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSettings(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setSaving(true);
            await axios.post(`${API_BASE}/settings/api/settings`, settings);
            alert('Settings saved successfully!');
        } catch (err) {
            alert('Failed to save settings');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-4">Loading settings...</div>;
    if (error) return <div className="p-4 text-red-500">{error}</div>;

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-6 flex items-center"><SettingsIcon className="mr-2" /> Settings</h1>
            
            <div className="max-w-2xl bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md border border-gray-100">
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Currency Symbol</label>
                        <select 
                            name="currencySymbol" 
                            value={settings.currencySymbol} 
                            onChange={handleChange}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                        >
                            <option value="₹">₹ (INR)</option>
                            <option value="$">$ (USD)</option>
                            <option value="€">€ (EUR)</option>
                            <option value="£">£ (GBP)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Fiscal Year Start</label>
                        <input 
                            type="text" 
                            name="fiscalYearStart" 
                            value={settings.fiscalYearStart} 
                            onChange={handleChange}
                            placeholder="MM-DD"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                        />
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Format: MM-DD (e.g., 04-01 for April 1st)</p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">Default Account</label>
                        <select 
                            name="defaultAccountId" 
                            value={settings.defaultAccountId} 
                            onChange={handleChange}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                        >
                            <option value="">-- Select an Account --</option>
                            {accounts.map(account => (
                                <option key={account.id} value={account.id}>{account.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="pt-4">
                        <button 
                            type="submit" 
                            disabled={saving}
                            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {saving ? 'Saving...' : <><Save className="mr-2 h-5 w-5" /> Save Settings</>}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Settings;
