import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { GEMINI_CONFIG } from "@/lib/config";
import { CheckCircle2, XCircle, AlertCircle, Loader2 } from "lucide-react";

/**
 * Gemini API Status Checker
 * This component helps diagnose API configuration issues
 * Only use in development for debugging
 */
const GeminiAPIStatus = () => {
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState<{
    status: 'success' | 'error' | 'warning' | null;
    message: string;
    details?: any;
  }>({ status: null, message: '' });

  // Check API key configuration
  const checkConfig = () => {
    const issues: string[] = [];
    
    if (!GEMINI_CONFIG.apiKey) {
      issues.push('API key is not configured');
    } else if (GEMINI_CONFIG.apiKey === 'your_gemini_api_key_here') {
      issues.push('Using placeholder API key');
    } else if (!GEMINI_CONFIG.apiKey.startsWith('AIza')) {
      issues.push('API key format looks incorrect');
    }
    
    return issues;
  };

  const testAPI = async () => {
    setTesting(true);
    setResult({ status: null, message: 'Testing API...' });

    try {
      const configIssues = checkConfig();
      if (configIssues.length > 0) {
        setResult({
          status: 'error',
          message: 'Configuration issues found',
          details: configIssues
        });
        setTesting(false);
        return;
      }

      console.log('🧪 Testing Gemini API...');
      
      const response = await fetch(`${GEMINI_CONFIG.apiUrl}?key=${GEMINI_CONFIG.apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: "Say 'API test successful' in exactly those words."
            }]
          }],
          generationConfig: {
            temperature: 0.1,
            maxOutputTokens: 50
          }
        })
      });

      console.log('🧪 Test Response Status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { message: errorText };
        }

        console.error('🧪 Test Failed:', errorData);

        const errorMessage = errorData?.error?.message || 
                            errorData?.message || 
                            'Unknown error';

        setResult({
          status: 'error',
          message: `API Error (${response.status}): ${errorMessage}`,
          details: errorData
        });
        setTesting(false);
        return;
      }

      const data = await response.json();
      console.log('🧪 Test Response:', data);

      if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
        setResult({
          status: 'success',
          message: 'API is working correctly! ✅',
          details: data.candidates[0].content.parts[0].text
        });
      } else {
        setResult({
          status: 'warning',
          message: 'API responded but format is unexpected',
          details: data
        });
      }
    } catch (error) {
      console.error('🧪 Test Error:', error);
      setResult({
        status: 'error',
        message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: error
      });
    } finally {
      setTesting(false);
    }
  };

  const configIssues = checkConfig();

  return (
    <Card className="p-4 max-w-2xl mx-auto my-4">
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold mb-2">Gemini API Status</h3>
          <p className="text-sm text-muted-foreground">
            Debug tool to check API configuration
          </p>
        </div>

        {/* Configuration Status */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Configuration</h4>
          <div className="grid gap-2 text-sm">
            <div className="flex items-center justify-between">
              <span>API Key Set:</span>
              {GEMINI_CONFIG.apiKey ? (
                <Badge variant="default" className="gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  Yes
                </Badge>
              ) : (
                <Badge variant="destructive" className="gap-1">
                  <XCircle className="w-3 h-3" />
                  No
                </Badge>
              )}
            </div>
            
            {GEMINI_CONFIG.apiKey && (
              <div className="flex items-center justify-between">
                <span>API Key Preview:</span>
                <code className="text-xs bg-muted px-2 py-1 rounded">
                  {GEMINI_CONFIG.apiKey.substring(0, 10)}...
                </code>
              </div>
            )}

            <div className="flex items-center justify-between">
              <span>Model:</span>
              <code className="text-xs bg-muted px-2 py-1 rounded">
                {GEMINI_CONFIG.model}
              </code>
            </div>

            <div className="flex items-center justify-between">
              <span>API Version:</span>
              <code className="text-xs bg-muted px-2 py-1 rounded">
                {GEMINI_CONFIG.apiUrl.includes('/v1beta/') ? 'v1beta (Beta)' : 'v1 (Stable)'}
              </code>
            </div>
          </div>

          {configIssues.length > 0 && (
            <div className="mt-2 p-2 bg-destructive/10 border border-destructive/20 rounded">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-destructive mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-destructive">Configuration Issues:</p>
                  <ul className="text-xs text-destructive/80 list-disc list-inside mt-1">
                    {configIssues.map((issue, i) => (
                      <li key={i}>{issue}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Test Button */}
        <Button 
          onClick={testAPI} 
          disabled={testing || configIssues.length > 0}
          className="w-full"
        >
          {testing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Testing...
            </>
          ) : (
            'Test API Connection'
          )}
        </Button>

        {/* Test Result */}
        {result.status && (
          <div className={`p-3 rounded-lg border ${
            result.status === 'success' ? 'bg-green-50 border-green-200 dark:bg-green-950 dark:border-green-800' :
            result.status === 'warning' ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950 dark:border-yellow-800' :
            'bg-red-50 border-red-200 dark:bg-red-950 dark:border-red-800'
          }`}>
            <div className="flex items-start gap-2">
              {result.status === 'success' && <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />}
              {result.status === 'warning' && <AlertCircle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />}
              {result.status === 'error' && <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5" />}
              <div className="flex-1">
                <p className="text-sm font-medium">{result.message}</p>
                {result.details && (
                  <details className="mt-2">
                    <summary className="text-xs cursor-pointer hover:underline">
                      Show details
                    </summary>
                    <pre className="mt-2 text-xs bg-black/5 dark:bg-white/5 p-2 rounded overflow-auto max-h-40">
                      {typeof result.details === 'string' 
                        ? result.details 
                        : JSON.stringify(result.details, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
          <p><strong>To fix API issues:</strong></p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li>Get API key from <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="underline">Google AI Studio</a></li>
            <li>Add to <code className="bg-muted px-1 rounded">.env</code> file: <code className="bg-muted px-1 rounded">VITE_GEMINI_API_KEY=your_key</code></li>
            <li>Restart dev server: <code className="bg-muted px-1 rounded">npm run dev</code></li>
          </ol>
        </div>
      </div>
    </Card>
  );
};

export default GeminiAPIStatus;
