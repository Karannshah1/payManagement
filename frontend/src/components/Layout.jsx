import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Receipt, Wallet, PieChart, Menu, Sun, Moon, Landmark, Trophy, Calculator, Users, Repeat, Bell, TrendingUp, UploadCloud, FileBarChart, Settings } from 'lucide-react';

const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme === 'dark' || (!storedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    if (!isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Expenses', path: '/expenses', icon: <Receipt size={20} /> },
    { name: 'Income', path: '/income', icon: <Wallet size={20} /> },
    { name: 'Accounts', path: '/accounts', icon: <Landmark size={20} /> },
    { name: 'Budgets', path: '/budgets', icon: <PieChart size={20} /> },
    { name: 'Goals', path: '/goals', icon: <Trophy size={20} /> },
    { name: 'EMI Tracker', path: '/emi', icon: <Calculator size={20} /> },
    { name: 'Split Expenses', path: '/splits', icon: <Users size={20} /> },
    { name: 'Subscriptions', path: '/subscriptions', icon: <Repeat size={20} /> },
    { name: 'Reminders', path: '/reminders', icon: <Bell size={20} /> },
    { name: 'Analytics', path: '/analytics', icon: <TrendingUp size={20} /> },
    { name: 'Smart Import', path: '/import', icon: <UploadCloud size={20} /> },
    { name: 'Reports', path: '/reports', icon: <FileBarChart size={20} /> },
    { name: 'Settings', path: '/settings', icon: <Settings size={20} /> },
  ];

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans transition-colors duration-200">
      {/* Sidebar */}
      <aside className={`bg-white dark:bg-gray-800 shadow-md transition-all duration-300 ${isSidebarOpen ? 'w-64' : 'w-0 -translate-x-full md:w-20 md:translate-x-0'} fixed md:relative z-20 h-full flex flex-col overflow-hidden`}>
        <div className="h-16 flex items-center justify-center border-b dark:border-gray-700">
          <span className={`text-xl font-bold whitespace-nowrap text-indigo-600 dark:text-indigo-400 ${!isSidebarOpen && 'md:hidden'}`}>
            PayManagement
          </span>
          {(!isSidebarOpen) && <span className="hidden md:block text-xl font-bold text-indigo-600 dark:text-indigo-400">PM</span>}
        </div>
        <nav className="flex-1 py-4">
          <ul className="space-y-2 px-2">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className={`flex items-center p-3 rounded-lg hover:bg-indigo-50 dark:hover:bg-gray-700 transition-colors ${isActive ? 'bg-indigo-100 dark:bg-gray-700 text-indigo-600 dark:text-indigo-400 font-medium' : ''}`}
                    title={!isSidebarOpen ? link.name : ''}
                  >
                    <span className="flex-shrink-0">{link.icon}</span>
                    <span className={`ml-3 whitespace-nowrap transition-opacity ${!isSidebarOpen ? 'opacity-0 md:hidden' : 'opacity-100'}`}>
                      {link.name}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden w-full">
        {/* Top Navbar */}
        <header className="h-16 bg-white dark:bg-gray-800 shadow-sm flex items-center justify-between px-4 z-10 transition-colors duration-200">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
            >
              <Menu size={24} />
            </button>
            <div className="hidden sm:block">
               <input 
                  type="text" 
                  placeholder="Quick Add (e.g. ₹500 Lunch)" 
                  className="px-4 py-2 border rounded-md dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-64 md:w-96 text-sm"
               />
            </div>
          </div>
          <div>
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
              title="Toggle Dark Mode"
            >
              {isDarkMode ? <Sun size={20} className="text-yellow-500" /> : <Moon size={20} className="text-indigo-600" />}
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-4 md:p-6 bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
          {children}
        </main>
      </div>
      
      {/* Mobile Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-10 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        ></div>
      )}
    </div>
  );
};

export default Layout;
