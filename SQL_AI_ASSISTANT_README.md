# SQL AI Assistant for PesacodeDB

## Overview

An AI-powered SQL assistant has been integrated into your PesacodeDB RDBMS application. This assistant helps users write SQL queries, explain existing queries, and optimize database operations using Google's Gemini AI.

## Features

### 🤖 AI-Powered Query Generation
- Convert natural language requests into valid SQL queries
- Context-aware of your current database schema
- Provides explanations along with generated queries

### 📚 Query Templates
- Pre-built templates for common SQL operations
- Organized by category (DDL, DML, DQL)
- Click-to-insert functionality

### 🔍 Query Explanation
- Paste any SQL query to get a plain-English explanation
- Breaks down complex queries into understandable parts
- Great for learning and understanding existing code

### ⚡ Query Optimization
- Submit queries for optimization suggestions
- Get best practices recommendations
- Improve query performance

### 📊 Schema Awareness
- Real-time access to your database schema
- Table and column information display
- Constraint and data type visibility

## Installation & Setup

### 1. Get Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cd frontend
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```env
   REACT_APP_GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Restart the Development Server

```bash
# Stop the current server (Ctrl+C)
# Then restart it
npm start
# or
yarn start
```

## Usage Guide

### Basic Chat Interface

1. **Expand the Assistant**: Click on the "SQL AI Assistant" card to expand it
2. **Choose a Tab**:
   - **Chat**: Interact with the AI assistant
   - **Templates**: Browse pre-built query templates
   - **Schema**: View your current database structure

### Generating Queries

**Example prompts:**
```
"Create a table for storing customer information with email, name, and phone"
"Write a query to select all active users"
"How do I join the users and orders tables?"
"Insert a new product with id 1, name 'Laptop', and price 999"
```

### Explaining Queries

Click the "Explain" button or type:
```
Explain this query: SELECT u.name, o.total FROM users u INNER JOIN orders o ON u.id = o.user_id
```

### Optimizing Queries

Click the "Optimize" button or type:
```
Optimize this query: SELECT * FROM users WHERE name LIKE '%john%'
```

### Using Templates

1. Navigate to the **Templates** tab
2. Browse available templates by category
3. Click any template to view details and examples
4. Use the "Insert to Editor" button to add it to your SQL editor

### Quick Actions

The assistant provides three quick action buttons:

- **Generate**: Start writing a SQL query from scratch
- **Explain**: Get an explanation of a SQL query
- **Optimize**: Get optimization suggestions

## File Structure

```
frontend/src/
├── components/
│   └── SQLAssistant.jsx          # Main AI assistant component
├── lib/
│   ├── config.js                 # API and app configuration
│   ├── gemini.js                 # Gemini AI integration
│   ├── ai-utils.js               # Utility functions (rate limiting, validation)
│   └── sql-knowledge-base.js     # SQL templates and knowledge base
```

## Features in Detail

### Rate Limiting
- Prevents API abuse
- 10 requests per minute
- 50 requests per hour

### Safety Features
- Input sanitization
- SQL injection prevention
- Spam detection
- Content filtering

### Error Handling
- Graceful fallbacks for API errors
- Clear error messages
- Network error detection
- API quota management

## Architecture

### Components Created

1. **SQLAssistant.jsx**
   - Main UI component
   - Handles user interactions
   - Manages conversation state
   - Integrates with the SQL editor

2. **lib/gemini.js**
   - Gemini API integration
   - Query generation functions
   - Response parsing and error handling

3. **lib/ai-utils.js**
   - Rate limiting logic
   - Input validation
   - Text sanitization
   - SQL query formatting

4. **lib/sql-knowledge-base.js**
   - SQL reference documentation
   - Query templates
   - Schema context building
   - Help topics

5. **lib/config.js**
   - Centralized configuration
   - API settings
   - Rate limit settings

## Customization

### Adjust AI Behavior

Edit `frontend/src/lib/config.js`:

```javascript
export const AI_CONFIG = {
  maxQueryLength: 1000,        // Max user input length
  maxResponseLength: 2000,     // Max AI response length
  temperature: 0.7,            // AI creativity (0-1)
  maxOutputTokens: 1024,       // Max response tokens
};
```

### Modify Rate Limits

```javascript
export const RATE_LIMIT_CONFIG = {
  maxRequestsPerMinute: 10,
  maxRequestsPerHour: 50,
};
```

### Add Custom Templates

Edit `frontend/src/lib/sql-knowledge-base.js`:

```javascript
export const SQL_QUERY_TEMPLATES = [
  {
    title: "Your Template Name",
    category: "DQL", // or DDL, DML
    template: "SELECT [columns] FROM [table]",
    example: "SELECT * FROM users",
    description: "Your description here"
  },
  // ... more templates
];
```

## Troubleshooting

### "API key is not configured"
- Verify `.env` file exists in `frontend/` directory
- Check that `REACT_APP_GEMINI_API_KEY` is set correctly
- Restart the development server after changing `.env`

### "Rate limit exceeded"
- Wait a moment before making another request
- Check `RATE_LIMIT_CONFIG` in `config.js`
- Consider increasing limits for development

### "Network error"
- Check your internet connection
- Verify the Gemini API is accessible
- Check for firewall/proxy issues

### Assistant not appearing
- Ensure all files were created correctly
- Check browser console for errors
- Verify imports in `DatabaseInterface.jsx`

## Best Practices

1. **Be Specific**: Provide clear, detailed prompts
2. **Include Context**: Mention table names and columns when relevant
3. **Review Generated Queries**: Always verify AI-generated SQL before executing
4. **Use Templates**: Start with templates for common patterns
5. **Learn from Explanations**: Use the explain feature to understand SQL better

## API Costs

The Gemini API offers a generous free tier:
- 60 requests per minute
- 1,500 requests per day (for free tier)

Monitor your usage at [Google AI Studio](https://aistudio.google.com/).

## Privacy & Security

- Queries are sent to Google's Gemini API
- No sensitive data should be included in prompts
- API calls are logged by Google for service improvement
- Use environment variables (not in version control) for API keys

## Future Enhancements

Potential improvements:
- Query execution preview
- Multi-step query building
- Visual query builder integration
- Query history with AI suggestions
- Custom knowledge base for your specific domain
- Voice input support
- Query performance prediction

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in the browser console
3. Verify API key configuration
4. Check the [Gemini API documentation](https://ai.google.dev/docs)

## License

This AI assistant integration is part of the PesacodeDB project.

---

**Happy Querying! 🚀**
