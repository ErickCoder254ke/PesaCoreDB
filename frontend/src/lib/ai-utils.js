import { RATE_LIMIT_CONFIG } from './config';

/**
 * Simple rate limiter to prevent API abuse
 */
class RateLimiter {
  constructor() {
    this.requests = [];
  }

  canMakeRequest() {
    const now = Date.now();
    const oneMinuteAgo = now - 60 * 1000;
    const oneHourAgo = now - 60 * 60 * 1000;

    // Clean old requests
    this.requests = this.requests.filter(time => time > oneHourAgo);

    const recentRequests = this.requests.filter(time => time > oneMinuteAgo);

    // Check limits
    if (recentRequests.length >= RATE_LIMIT_CONFIG.maxRequestsPerMinute) {
      return false;
    }

    if (this.requests.length >= RATE_LIMIT_CONFIG.maxRequestsPerHour) {
      return false;
    }

    // Add current request
    this.requests.push(now);
    return true;
  }

  reset() {
    this.requests = [];
  }
}

export const chatRateLimiter = new RateLimiter();

/**
 * Sanitize user input to prevent injection attacks
 */
export function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  
  // Trim whitespace
  let sanitized = input.trim();
  
  // Remove any script tags or HTML
  sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  sanitized = sanitized.replace(/<[^>]*>/g, '');
  
  return sanitized;
}

/**
 * Check if input is likely spam
 */
export function isLikelySpam(input) {
  const spamIndicators = [
    /(.)\1{10,}/, // Repeated characters
    /https?:\/\//gi, // URLs (could relax this for SQL assistant)
    /^\s*$/,  // Empty or whitespace only
  ];

  return spamIndicators.some(pattern => pattern.test(input));
}

/**
 * Track AI interactions for analytics (localStorage based)
 */
export function trackAIInteraction(eventType, data = {}) {
  try {
    const interactions = JSON.parse(localStorage.getItem('ai-interactions') || '[]');
    interactions.push({
      timestamp: new Date().toISOString(),
      eventType,
      ...data,
    });
    
    // Keep only last 100 interactions
    if (interactions.length > 100) {
      interactions.shift();
    }
    
    localStorage.setItem('ai-interactions', JSON.stringify(interactions));
  } catch (error) {
    console.error('Failed to track interaction:', error);
  }
}

/**
 * Format SQL query for better readability
 */
export function formatSQLForDisplay(sql) {
  if (!sql) return '';
  
  const keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 
                    'ON', 'AND', 'OR', 'ORDER BY', 'GROUP BY', 'HAVING', 'INSERT', 'UPDATE', 
                    'DELETE', 'CREATE', 'DROP', 'ALTER', 'TABLE', 'VALUES', 'SET'];
  
  let formatted = sql;
  keywords.forEach(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
    formatted = formatted.replace(regex, keyword);
  });
  
  return formatted;
}

/**
 * Extract table names from SQL query
 */
export function extractTableNames(sql) {
  const tablePattern = /(?:FROM|JOIN|INTO|UPDATE|TABLE)\s+([a-zA-Z_][a-zA-Z0-9_]*)/gi;
  const matches = [];
  let match;
  
  while ((match = tablePattern.exec(sql)) !== null) {
    if (match[1] && !matches.includes(match[1].toLowerCase())) {
      matches.push(match[1].toLowerCase());
    }
  }
  
  return matches;
}

/**
 * Validate SQL query structure (basic validation)
 */
export function validateSQLSyntax(sql) {
  if (!sql || sql.trim().length === 0) {
    return { valid: false, error: 'Query cannot be empty' };
  }

  const trimmed = sql.trim().toUpperCase();
  const validStarters = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'SHOW', 'DESC'];
  
  if (!validStarters.some(starter => trimmed.startsWith(starter))) {
    return { 
      valid: false, 
      error: 'Query must start with a valid SQL keyword (SELECT, INSERT, UPDATE, etc.)' 
    };
  }

  // Check for balanced parentheses
  const openParens = (sql.match(/\(/g) || []).length;
  const closeParens = (sql.match(/\)/g) || []).length;
  
  if (openParens !== closeParens) {
    return { valid: false, error: 'Unbalanced parentheses in query' };
  }

  return { valid: true };
}
