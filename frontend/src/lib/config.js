/**
 * Configuration for external services
 */

// Debug: Log environment variables
console.log('🔍 Environment Check:', {
  backendUrl: process.env.REACT_APP_BACKEND_URL,
  useBackendAI: true
});

// Gemini AI Configuration
// Now proxied through backend for security
export const GEMINI_CONFIG = {
  useBackendProxy: true, // Always use backend proxy for AI requests
  model: 'gemini-flash-latest',
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
