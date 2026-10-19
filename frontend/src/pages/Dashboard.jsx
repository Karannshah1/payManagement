import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [dailyTrend, setDailyTrend] = useState([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [predictive, setPredictive] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Execute API calls concurrently
        const [summaryRes, trendRes, categoryRes] = await Promise.all([
          axios.get(`${API_BASE}/api/dashboard/summary`),
          axios.get(`${API_BASE}/api/dashboard/daily-trend`),
          axios.get(`${API_BASE}/api/dashboard/category-breakdown`)
        ]);
        
        setSummary(summaryRes.data);
        setDailyTrend(trendRes.data);
        setCategoryBreakdown(categoryRes.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-4rem)] bg-gray-50 dark:bg-gray-900">
        <div className="text-xl font-semibold text-gray-600 animate-pulse">Loading Dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-[calc(100vh-4rem)] bg-gray-50 dark:bg-gray-900">
        <div className="text-lg font-semibold text-red-500 bg-red-50 px-6 py-4 rounded-lg shadow-sm border border-red-100">
          {error}
        </div>
      </div>
    );
  }

  // Fallback colors for the pie chart
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6'];

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-8">Dashboard</h1>

        {/* Top Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between transition-transform hover:scale-105">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total Income</p>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                ₹{summary?.totalIncome?.toLocaleString('en-IN') || 0}
              </h3>
            </div>
            <div className="p-3 bg-green-50 rounded-full text-green-500">
              <TrendingUp size={24} />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between transition-transform hover:scale-105">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total Expenses</p>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                ₹{summary?.totalExpenses?.toLocaleString('en-IN') || 0}
              </h3>
            </div>
            <div className="p-3 bg-red-50 rounded-full text-red-500">
              <TrendingDown size={24} />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between transition-transform hover:scale-105">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Net Savings</p>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                ₹{summary?.netSavings?.toLocaleString('en-IN') || 0}
              </h3>
            </div>
            <div className="p-3 bg-blue-50 rounded-full text-blue-500">
              <DollarSign size={24} />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between transition-transform hover:scale-105">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Budget Health</p>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-100">
                {summary?.budgetHealth || 'Good'}
              </h3>
            </div>
            <div className="p-3 bg-purple-50 rounded-full text-purple-500">
              <Activity size={24} />
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Daily Spend Trend */}
          <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-6">Daily Spend Trend</h2>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={dailyTrend} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#6b7280', fontSize: 12 }} 
                    dy={10}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                    tickFormatter={(value) => `₹${value}`}
                    dx={-10}
                  />
                  <Tooltip
                    formatter={(value) => [`₹${value}`, 'Amount']}
                    contentStyle={{ 
                      borderRadius: '8px', 
                      border: 'none', 
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' 
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="amount" 
                    stroke="#3b82f6" 
                    strokeWidth={3} 
                    dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} 
                    activeDot={{ r: 6, strokeWidth: 0 }} 
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Category Breakdown */}
          <div className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100 mb-6">Category Breakdown</h2>
            <div className="h-80 w-full flex justify-center items-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryBreakdown}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={110}
                    paddingAngle={5}
                    dataKey="value"
                    nameKey="name"
                    labelLine={false}
                    label={({ name, percent }) => percent > 0.05 ? `${name} ${(percent * 100).toFixed(0)}%` : ''}
                  >
                    {categoryBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`₹${value}`, 'Amount']}
                    contentStyle={{ 
                      borderRadius: '8px', 
                      border: 'none', 
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)' 
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

