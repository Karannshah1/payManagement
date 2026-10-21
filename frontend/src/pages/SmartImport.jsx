import API_BASE from '../config';
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, MessageSquare, CheckCircle2, Wallet } from 'lucide-react';

const SmartImport = () => {
  const [smsText, setSmsText] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const res = await axios.get(`${API_BASE}/accounts/api/accounts`);
      setAccounts(res.data || []);
      if (res.data && res.data.length > 0 && !selectedAccount) {
        setSelectedAccount(res.data[0].id);
      }
    } catch (e) {
      console.error('Error loading accounts:', e);
    }
  };

  const handleSmsSubmit = async (e) => {
    e.preventDefault();
    if (!smsText.trim()) return;
    
    setLoading(true);
    setError('');
    setParsedData(null);
    setSuccessMsg('');

    try {
      const response = await axios.post(`${API_BASE}/api/import/ai-parse`, { text: smsText });
      setParsedData(response.data.parsed);
    } catch (err) {
      setError('AI Parsing failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError('');
    setParsedData(null);
    setSuccessMsg('');

    try {
      const response = await axios.post(`${API_BASE}/api/import/ai-parse`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setParsedData(response.data.parsed);
    } catch (err) {
      setError('PDF Parsing failed: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSaveToDatabase = async () => {
    if (!parsedData) return;
    
    setLoading(true);
    try {
      if (parsedData.type === 'income') {
        await axios.post(`${API_BASE}/income/api/income`, {
          source: parsedData.description,
          amount: parseFloat(parsedData.amount),
          account_id: selectedAccount,
          date: new Date().toISOString().split('T')[0]
        });
      } else {
        await axios.post(`${API_BASE}/expenses/api/expenses`, {
          description: parsedData.description,
          amount: parseFloat(parsedData.amount),
          category: parsedData.category,
          account_id: selectedAccount,
          date: new Date().toISOString().split('T')[0]
        });
      }
      setSuccessMsg(`Successfully saved ${parsedData.type} to database!`);
      setParsedData(null);
      setSmsText('');
    } catch (err) {
      setError('Failed to save to database: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-8 text-gray-900 dark:text-gray-100">Smart Import Hub</h1>
      
      {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">{error}</div>}
      {successMsg && <div className="mb-4 p-3 bg-green-100 text-green-700 flex items-center gap-2 rounded-lg text-sm"><CheckCircle2 className="w-4 h-4"/>{successMsg}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        
        {/* Paste UPI SMS (AI Powered) */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-50 text-purple-600 rounded-lg">
              <MessageSquare className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">AI Smart Parse (SMS/Text)</h2>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Paste any transaction SMS, copied text, or quick note. Our AI will instantly extract the merchant, amount, and perfectly categorize it!
          </p>
          
          <form onSubmit={handleSmsSubmit}>
            <textarea 
              className="w-full border p-3 text-sm focus:ring-2 focus:ring-purple-500 rounded-lg dark:bg-gray-700 dark:border-gray-600 dark:text-white resize-none mb-3"
              rows="4"
              placeholder="e.g. Spent 1200 on domino's pizza for dinner yesterday..."
              value={smsText}
              onChange={(e) => setSmsText(e.target.value)}
            />
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-purple-600 text-white py-2.5 rounded-lg font-medium hover:bg-purple-700 transition disabled:opacity-50 shadow-sm"
            >
              {loading ? 'AI is thinking...' : 'Extract with AI'}
            </button>
          </form>
        </div>

        {/* PDF Document Upload */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-lg"><FileText className="w-6 h-6" /></div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">PDF Bank Statement Upload</h2>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Upload a PDF receipt or mini-statement. The AI will extract the primary transaction and categorize it instantly.
          </p>
          
          <div 
            className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-8 text-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            onClick={() => fileInputRef.current.click()}
          >
            <UploadCloud className="w-8 h-8 mx-auto text-blue-500 mb-2" />
            <span className="text-sm text-gray-600 dark:text-gray-300 font-medium">Click to upload PDF or Text File</span>
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileUpload} 
              className="hidden" 
              accept=".pdf,.txt" 
            />
          </div>
        </div>
      </div>

      {parsedData && (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-500" /> 
            AI Extraction Result
          </h3>
          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-sm mb-4 grid grid-cols-2 gap-2">
            <p><strong>Merchant:</strong> {parsedData.description}</p>
            <p><strong>Amount:</strong> ₹{parsedData.amount}</p>
            <p><strong>Category:</strong> {parsedData.category}</p>
            <p><strong>Type:</strong> <span className="capitalize">{parsedData.type}</span></p>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1.5">
              <Wallet size={16} /> Link to Account
            </label>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="w-full md:w-80 border dark:border-gray-600 dark:bg-gray-700 dark:text-white p-2.5 rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
            >
              {accounts.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} (₹{a.balance?.toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <button 
            onClick={handleSaveToDatabase}
            disabled={loading}
            className="w-full md:w-auto px-6 bg-green-600 text-white py-2.5 rounded-lg font-medium hover:bg-green-700 transition shadow-sm"
          >
            Looks Correct — Save to Database
          </button>
        </div>
      )}
    </div>
  );
};

export default SmartImport;
