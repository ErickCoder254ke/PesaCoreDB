/**
 * Configuration for external services
 */

// Debug: Log environment variables
console.log('🔍 Environment Check:', {
  hasApiKey: !!process.env.REACT_APP_GEMINI_API_KEY,
  apiKeyPrefix: process.env.REACT_APP_GEMINI_API_KEY?.substring(0, 10) + '...',
  backendUrl: process.env.REACT_APP_BACKEND_URL
});

// Gemini AI Configuration
export const GEMINI_CONFIG = {
  apiKey: process.env.REACT_APP_GEMINI_API_KEY || 'your_gemini_api_key_here',
  model: 'gemini-flash-latest',
  apiUrl: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent',
  maxRetries: 2,
  timeout: 30000, // 30 seconds
};

// AI Configuration
export const AI_CONFIG = {
  maxQueryLength: 1000,
  maxResponseLength: 2000,
  temperature: 0.7,
  maxOutputTokens: 1024,
};

// Rate Limiting Configuration
export const RATE_LIMIT_CONFIG = {
  maxRequestsPerMinute: 10,
  maxRequestsPerHour: 50,
};

// Contact Configuration (optional - for fallback)
export const CONTACT_CONFIG = {
  email: 'support@pesacodedb.com',
  whatsappUrl: 'https://wa.me/your-number',
};
