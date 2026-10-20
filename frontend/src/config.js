// Central API and Service Configuration
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export default API_BASE;
