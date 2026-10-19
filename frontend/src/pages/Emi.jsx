import API_BASE from '../config';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar, CheckCircle } from 'lucide-react';

const Emi = () => {
  const [emis, setEmis] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmis();
  }, []);

  const fetchEmis = async () => {
    try {
      const response = await axios.get(`${API_BASE}/emi/api/emi`);
      setEmis(response.data);
    } catch (error) {
      console.error('API failed, using dummy data', error);
      setEmis([
        { id: 1, name: 'Home Loan', totalTenure: 240, completedMonths: 45, emiAmount: 35000 },
        { id: 2, name: 'Car Loan', totalTenure: 60, completedMonths: 12, emiAmount: 15500 },
        { id: 3, name: 'Personal Loan', totalTenure: 36, completedMonths: 35, emiAmount: 8000 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handlePay = (id) => {
    setEmis(emis.map(emi => {
      if (emi.id === id && emi.completedMonths < emi.totalTenure) {
        return { ...emi, completedMonths: emi.completedMonths + 1 };
      }
      return emi;
    }));
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6 flex items-center"><Calendar className="mr-2" /> EMI Management</h1>
      
      <div className="space-y-4">
        {loading ? <p>Loading...</p> : emis.map((emi) => {
          const remainingMonths = emi.totalTenure - emi.completedMonths;
          const progress = ((emi.completedMonths / emi.totalTenure) * 100).toFixed(1);
          
          return (
            <div key={emi.id} className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 rounded-lg shadow-md flex flex-col md:flex-row items-center justify-between">
              <div className="flex-1 w-full md:w-auto mb-4 md:mb-0">
                <h3 className="text-xl font-semibold mb-2">{emi.name}</h3>
                <p className="text-gray-600 mb-2">₹{emi.emiAmount.toLocaleString()} / month</p>
                
                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-2 space-x-4">
                  <span>Tenure: {emi.totalTenure} months</span>
                  <span>Completed: {emi.completedMonths} months</span>
                  <span>Remaining: {remainingMonths} months</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2 max-w-md">
                  <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${progress}%` }}></div>
                </div>
              </div>
              
              <div>
                <button 
                  onClick={() => handlePay(emi.id)}
                  disabled={remainingMonths === 0}
                  className={`px-6 py-2 rounded font-medium flex items-center ${
                    remainingMonths === 0 
                    ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed' 
                    : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  }`}
                >
                  <CheckCircle className="mr-2 h-5 w-5" />
                  {remainingMonths === 0 ? 'Completed' : 'Pay EMI'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Emi;
