import { GEMINI_CONFIG, AI_CONFIG } from './config';

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
 * Generate AI response using Gemini API
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

  // Check API key
  if (!GEMINI_CONFIG.apiKey || GEMINI_CONFIG.apiKey === 'your_gemini_api_key_here') {
    return {
      success: false,
      error: 'Gemini API key is not configured. Please set REACT_APP_GEMINI_API_KEY in your environment.',
      errorType: 'api_key',
    };
  }

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
    // Build the prompt with context
    const fullPrompt = buildPrompt(userQuery, contextData, systemPrompt);

    console.log('🤖 Sending request to Gemini AI...');

    const response = await fetch(
      `${GEMINI_CONFIG.apiUrl}?key=${GEMINI_CONFIG.apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: fullPrompt
            }]
          }],
          generationConfig: {
            temperature,
            maxOutputTokens,
            topP: 0.95,
            topK: 40,
          },
          safetySettings: [
            {
              category: 'HARM_CATEGORY_HARASSMENT',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            },
            {
              category: 'HARM_CATEGORY_HATE_SPEECH',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            },
            {
              category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            },
            {
              category: 'HARM_CATEGORY_DANGEROUS_CONTENT',
              threshold: 'BLOCK_MEDIUM_AND_ABOVE'
            }
          ]
        })
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('❌ Gemini API Error:', errorData);

      // Handle specific error types
      if (response.status === 429) {
        return {
          success: false,
          error: 'Rate limit exceeded. Please try again in a moment.',
          errorType: 'quota',
        };
      }

      if (response.status === 400) {
        return {
          success: false,
          error: errorData.error?.message || 'Invalid request to AI service',
          errorType: 'validation',
        };
      }

      if (response.status === 403) {
        return {
          success: false,
          error: 'API key is invalid or has insufficient permissions',
          errorType: 'api_key',
        };
      }

      return {
        success: false,
        error: errorData.error?.message || `API error: ${response.status}`,
        errorType: 'api_error',
      };
    }

    const data = await response.json();
    console.log('✅ Received response from Gemini');

    // Extract response text
    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
      const responseText = data.candidates[0].content.parts[0].text;
      
      // Check if response was blocked
      if (data.candidates[0].finishReason === 'SAFETY') {
        return {
          success: false,
          error: 'Response was blocked due to safety concerns. Please rephrase your question.',
          errorType: 'safety',
        };
      }

      return {
        success: true,
        message: responseText.trim(),
        metadata: {
          finishReason: data.candidates[0].finishReason,
          safetyRatings: data.candidates[0].safetyRatings,
        },
      };
    }

    // Unexpected response format
    console.error('❌ Unexpected response format:', data);
    return {
      success: false,
      error: 'Received unexpected response format from AI service',
      errorType: 'format_error',
    };

  } catch (error) {
    console.error('❌ Error calling Gemini API:', error);

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        success: false,
        error: 'Network error. Please check your internet connection.',
        errorType: 'network',
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
