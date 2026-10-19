import API_BASE from '../config';
import React, { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, MessageSquare, CheckCircle2 } from 'lucide-react';

const SmartImport = () => {
  const [smsText, setSmsText] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  
  const fileInputRef = useRef(null);

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
      await axios.post(`${API_BASE}/expenses/api/expenses/quick-add`, {
        text: `${parsedData.description} ${parsedData.amount} ${parsedData.category}`
      });
      setSuccessMsg(`Successfully saved ${parsedData.type} to database!`);
      setParsedData(null);
      setSmsText('');
    } catch (err) {
      setError('Failed to save to database.');
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
              className="w-full bg-purple-600 text-white py-2 rounded-lg font-medium hover:bg-purple-700 transition disabled:opacity-50"
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
          <h3 className="font-medium text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-500" /> 
            AI Extraction Result
          </h3>
          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg text-sm mb-3">
            <p><strong>Merchant:</strong> {parsedData.description}</p>
            <p><strong>Amount:</strong> ₹{parsedData.amount}</p>
            <p><strong>Category:</strong> {parsedData.category}</p>
            <p><strong>Type:</strong> <span className="capitalize">{parsedData.type}</span></p>
          </div>
          <button 
            onClick={handleSaveToDatabase}
            disabled={loading}
            className="w-full md:w-auto px-6 bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 transition"
          >
            Looks Correct - Save to Database
          </button>
        </div>
      )}
    </div>
  );
};

export default SmartImport;
