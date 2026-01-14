/**
 * API Client for PesacodeDB
 * Automatically adds API key to all requests
 */

import axios from 'axios';

// Get configuration from environment
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API_KEY = process.env.REACT_APP_API_KEY || '';
const REQUIRE_API_KEY = process.env.REACT_APP_REQUIRE_API_KEY !== 'false';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add API key
apiClient.interceptors.request.use(
  (config) => {
    // Add API key if required and available
    if (REQUIRE_API_KEY && API_KEY) {
      config.headers['X-API-Key'] = API_KEY;
    }
    
    // Log request in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`🔵 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        hasApiKey: !!config.headers['X-API-Key'],
        params: config.params,
        data: config.data,
      });
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }
    return response;
  },
  (error) => {
    // Enhanced error handling
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 403) {
        console.error('❌ Authentication Error: Invalid or missing API key');
        // You could redirect to a login page or show an error modal here
      } else if (status === 500) {
        console.error('❌ Server Error:', data.error || data.detail);
      } else {
        console.error(`❌ API Error (${status}):`, data.error || data.detail);
      }
    } else if (error.request) {
      // Request was made but no response received
      console.error('❌ Network Error: No response from server', {
        url: error.config?.url,
        method: error.config?.method,
      });
    } else {
      // Something else happened
      console.error('❌ Request Setup Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Export configured client
export default apiClient;

// Also export the base URL for direct use
export const API_BASE_URL = `${BACKEND_URL}/api`;
export const BACKEND_BASE_URL = BACKEND_URL;

// Helper function to check if API is configured correctly
export const checkApiConfiguration = () => {
  const config = {
    backendUrl: BACKEND_URL,
    hasApiKey: !!API_KEY,
    requiresApiKey: REQUIRE_API_KEY,
    isConfigured: !REQUIRE_API_KEY || (REQUIRE_API_KEY && !!API_KEY),
  };
  
  console.log('🔧 API Configuration:', config);
  
  if (REQUIRE_API_KEY && !API_KEY) {
    console.warn('⚠️ WARNING: API key is required but not configured!');
    console.warn('   Set REACT_APP_API_KEY in your .env file');
  }
  
  return config;
};

// Run configuration check in development
if (process.env.NODE_ENV === 'development') {
  checkApiConfiguration();
}
