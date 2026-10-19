import API_BASE from '../config';
import React, { useState } from 'react';
import axios from 'axios';
import { FileBarChart, Download, FileSpreadsheet, FileText } from 'lucide-react';

const Reports = () => {
  const [taxData, setTaxData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchTaxReport = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/reports/api/reports/tax?year=2026`);
      setTaxData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-8 text-gray-900 dark:text-gray-100 flex items-center"><FileBarChart className="mr-2" /> Reports & Export</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        {/* Advanced Tax Report Card */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border dark:border-gray-700">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Advanced Tax Report</h2>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-bold">New</span>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Automatically scan your transactions for 80C, 80D, and 80GG eligible deductions.
          </p>
          <button onClick={fetchTaxReport} className="w-full flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white p-2 rounded transition">
            {loading ? 'Scanning...' : 'Generate 2026 Tax Report'}
          </button>
          
          {taxData && (
            <div className="mt-4 border-t dark:border-gray-700 pt-4">
              <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">Eligible Deductions</h3>
              {Object.keys(taxData.sections).length === 0 ? (
                <p className="text-sm text-gray-500">No eligible tax deductions found yet.</p>
              ) : (
                <ul className="space-y-2 mb-3">
                  {Object.entries(taxData.sections).map(([section, amount]) => (
                    <li key={section} className="flex justify-between text-sm">
                      <span className="font-medium text-gray-600 dark:text-gray-400">Section {section}</span>
                      <span className="font-bold text-gray-800 dark:text-gray-200">?{amount.toLocaleString()}</span>
                    </li>
                  ))}
                </ul>
              )}
              <div className="flex justify-between font-bold text-green-600 border-t pt-2 dark:border-gray-700">
                <span>Total Savings Found:</span>
                <span>?{taxData.total_deductions.toLocaleString()}</span>
              </div>
            </div>
          )}
        </div>

        {/* Other Exports */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow border dark:border-gray-700">
           <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">Export Data</h2>
           <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">Download your raw transaction data as Excel or CSV for manual analysis.</p>
           <div className="space-y-3">
             <button className="w-full flex items-center justify-center bg-green-600 hover:bg-green-700 text-white p-2 rounded transition">
                <FileSpreadsheet className="w-4 h-4 mr-2" /> Download Excel (.xlsx)
             </button>
             <button className="w-full flex items-center justify-center bg-gray-600 hover:bg-gray-700 text-white p-2 rounded transition">
                <FileText className="w-4 h-4 mr-2" /> Download CSV (.csv)
             </button>
           </div>
        </div>

      </div>
    </div>
  );
};

export default Reports;
