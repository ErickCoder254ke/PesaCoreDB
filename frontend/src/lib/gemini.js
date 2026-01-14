import { GEMINI_CONFIG, AI_CONFIG } from './config';
import apiClient from './api-client';

/**
 * Validate user query before sending to AI
 */
export function validateUserQuery(query) {
  if (!query || typeof query !== 'string') {
    return { valid: false, error: 'Query must be a non-empty string' };
  }

  if (query.trim().length === 0) {
    return { valid: false, error: 'Query cannot be empty' };
  }

  if (query.length > AI_CONFIG.maxQueryLength) {
    return {
      valid: false,
      error: `Query too long (max ${AI_CONFIG.maxQueryLength} characters)`
    };
  }

  return { valid: true };
}

/**
 * Check if AI is configured on the backend
 */
export async function checkAIConfiguration() {
  try {
    const response = await apiClient.get('/ai/config');
    return response.data;
  } catch (error) {
    console.error('Error checking AI configuration:', error);
    return { enabled: false, message: 'Could not connect to backend' };
  }
}

/**
 * Generate AI response using backend proxy (more secure)
 * @param {string} userQuery - The user's question or request
 * @param {string} contextData - Context information (database schema, etc.)
 * @param {object} options - Additional options
 */
export async function generateAIResponse(userQuery, contextData = '', options = {}) {
  const {
    temperature = AI_CONFIG.temperature,
    maxOutputTokens = AI_CONFIG.maxOutputTokens,
    systemPrompt = '',
  } = options;

  // Validate query
  const validation = validateUserQuery(userQuery);
  if (!validation.valid) {
    return {
      success: false,
      error: validation.error,
      errorType: 'validation',
    };
  }

  try {
    console.log('🤖 Sending request to AI (via backend proxy)...');

    const response = await apiClient.post('/ai/generate', {
      prompt: userQuery,
      context: contextData,
      system_prompt: systemPrompt,
      temperature: temperature,
      max_tokens: maxOutputTokens,
    });

    const data = response.data;

    if (data.success) {
      console.log('✅ Received response from AI');
      return {
        success: true,
        message: data.message,
      };
    } else {
      console.error('❌ AI Error:', data.error);
      return {
        success: false,
        error: data.error || 'AI request failed',
        errorType: data.error_type || 'api_error',
      };
    }

  } catch (error) {
    console.error('❌ Error calling AI API:', error);

    // Check if it's a network error
    if (error.code === 'ERR_NETWORK' || !error.response) {
      return {
        success: false,
        error: 'Network error. Please check your connection to the backend.',
        errorType: 'network',
      };
    }

    // Check for specific HTTP errors
    if (error.response) {
      const { status, data } = error.response;

      if (status === 403) {
        return {
          success: false,
          error: 'Authentication failed. Check backend API key configuration.',
          errorType: 'auth',
        };
      }

      return {
        success: false,
        error: data?.error || `Request failed with status ${status}`,
        errorType: data?.error_type || 'api_error',
      };
    }

    return {
      success: false,
      error: error.message || 'Failed to generate AI response',
      errorType: 'exception',
    };
  }
}

/**
 * Build the full prompt with context and user query
 */
function buildPrompt(userQuery, contextData, systemPrompt) {
  let prompt = '';

  // Add system prompt if provided
  if (systemPrompt) {
    prompt += `${systemPrompt}\n\n`;
  }

  // Add context if provided
  if (contextData) {
    prompt += `Context:\n${contextData}\n\n`;
  }

  // Add user query
  prompt += `User Query: ${userQuery}`;

  return prompt;
}

/**
 * Generate SQL query suggestion based on natural language
 * Specialized function for SQL assistance
 */
export async function generateSQLFromNaturalLanguage(userRequest, schemaContext) {
  const systemPrompt = `You are a SQL expert assistant helping users write SQL queries for a relational database.
Given the database schema and a user's natural language request, generate a valid SQL query.

Rules:
1. Only generate valid SQL queries
2. Use the provided schema to ensure table and column names are correct
3. Provide brief explanations for complex queries
4. If the request is unclear, ask for clarification
5. Format the SQL query cleanly with proper indentation
6. Use standard SQL syntax
7. Include helpful comments in the SQL when necessary

Your response should include:
1. The SQL query (clearly marked)
2. A brief explanation of what the query does
3. Any important notes or warnings`;

  return generateAIResponse(userRequest, schemaContext, {
    systemPrompt,
    temperature: 0.3, // Lower temperature for more precise SQL generation
  });
}

/**
 * Explain a SQL query in natural language
 */
export async function explainSQLQuery(sqlQuery, schemaContext = '') {
  const systemPrompt = `You are a SQL expert assistant. Explain the given SQL query in clear, simple terms.
Break down what each part of the query does and what the overall result will be.

Make your explanation:
1. Clear and concise
2. Accessible to beginners
3. Structured (use bullet points or numbered lists)
4. Include what data will be returned`;

  return generateAIResponse(sqlQuery, schemaContext, {
    systemPrompt,
    temperature: 0.4,
  });
}

/**
 * Optimize a SQL query
 */
export async function optimizeSQLQuery(sqlQuery, schemaContext = '') {
  const systemPrompt = `You are a SQL optimization expert. Analyze the given query and suggest optimizations.

Provide:
1. The optimized SQL query
2. Explanation of what was optimized and why
3. Performance improvement notes
4. Best practices applied

Focus on:
- Index usage
- Join optimization
- Subquery optimization
- Avoiding full table scans
- Proper WHERE clause usage`;

  return generateAIResponse(sqlQuery, schemaContext, {
    systemPrompt,
    temperature: 0.3,
  });
}
