import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import apiClient, { BACKEND_BASE_URL } from '@/lib/api-client';

/**
 * AI Diagnostics Component
 * Shows the status of AI configuration and helps troubleshoot issues
 */
const AIDiagnostics = () => {
  const [checks, setChecks] = useState({
    backendReachable: { status: 'checking', message: 'Checking...' },
    aiEndpointExists: { status: 'checking', message: 'Checking...' },
    aiConfigured: { status: 'checking', message: 'Checking...' },
    canGenerateResponse: { status: 'checking', message: 'Checking...' },
  });
  const [isRunning, setIsRunning] = useState(false);

  const runDiagnostics = async () => {
    setIsRunning(true);
    const newChecks = { ...checks };

    // Check 1: Backend is reachable
    try {
      const response = await apiClient.get('/health');
      if (response.status === 200) {
        newChecks.backendReachable = {
          status: 'success',
          message: `✅ Backend is reachable at ${BACKEND_BASE_URL}`,
          data: response.data,
        };
      }
    } catch (error) {
      newChecks.backendReachable = {
        status: 'error',
        message: `❌ Cannot reach backend at ${BACKEND_BASE_URL}`,
        error: error.message,
      };
      setChecks(newChecks);
      setIsRunning(false);
      return; // Stop here if backend is not reachable
    }

    // Check 2: AI config endpoint exists
    try {
      const response = await apiClient.get('/ai/config');
      if (response.status === 200) {
        newChecks.aiEndpointExists = {
          status: 'success',
          message: '✅ AI endpoint exists',
          data: response.data,
        };

        // Check 3: AI is configured
        if (response.data.enabled) {
          newChecks.aiConfigured = {
            status: 'success',
            message: `✅ AI is configured (Model: ${response.data.model})`,
            data: response.data,
          };
        } else {
          newChecks.aiConfigured = {
            status: 'error',
            message: '❌ AI is not configured on backend',
            data: response.data,
            solution: 'Set GEMINI_API_KEY environment variable on backend',
          };
        }
      }
    } catch (error) {
      if (error.response?.status === 404) {
        newChecks.aiEndpointExists = {
          status: 'error',
          message: '❌ AI endpoint not found (old backend version)',
          solution: 'Deploy updated backend code with AI endpoints',
        };
        newChecks.aiConfigured = {
          status: 'skipped',
          message: '⏭️ Skipped (endpoint not available)',
        };
        newChecks.canGenerateResponse = {
          status: 'skipped',
          message: '⏭️ Skipped (endpoint not available)',
        };
        setChecks(newChecks);
        setIsRunning(false);
        return;
      } else {
        newChecks.aiEndpointExists = {
          status: 'error',
          message: '❌ Error checking AI endpoint',
          error: error.message,
        };
      }
    }

    // Check 4: Can generate a response
    if (newChecks.aiConfigured.status === 'success') {
      try {
        const response = await apiClient.post('/ai/generate', {
          prompt: 'Say "test successful" if you can read this',
          temperature: 0.3,
          max_tokens: 50,
        });

        if (response.data.success) {
          newChecks.canGenerateResponse = {
            status: 'success',
            message: '✅ Successfully generated AI response',
            data: response.data,
          };
        } else {
          newChecks.canGenerateResponse = {
            status: 'error',
            message: '❌ AI generation failed',
            error: response.data.error,
            errorType: response.data.error_type,
          };
        }
      } catch (error) {
        newChecks.canGenerateResponse = {
          status: 'error',
          message: '❌ Error generating AI response',
          error: error.response?.data?.error || error.message,
        };
      }
    } else {
      newChecks.canGenerateResponse = {
        status: 'skipped',
        message: '⏭️ Skipped (AI not configured)',
      };
    }

    setChecks(newChecks);
    setIsRunning(false);
  };

  useEffect(() => {
    runDiagnostics();
  }, []);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'checking':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'success':
        return <Badge className="bg-green-500">Working</Badge>;
      case 'error':
        return <Badge className="bg-red-500">Failed</Badge>;
      case 'checking':
        return <Badge className="bg-blue-500">Checking...</Badge>;
      default:
        return <Badge variant="secondary">Skipped</Badge>;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          🔍 AI Configuration Diagnostics
          <Button
            size="sm"
            variant="outline"
            onClick={runDiagnostics}
            disabled={isRunning}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRunning ? 'animate-spin' : ''}`} />
            Re-run
          </Button>
        </CardTitle>
        <CardDescription>
          Checking if AI features are properly configured
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Check 1: Backend Reachable */}
        <div className="flex items-start gap-3 p-3 border rounded-lg">
          {getStatusIcon(checks.backendReachable.status)}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <h4 className="font-semibold text-sm">Backend Connection</h4>
              {getStatusBadge(checks.backendReachable.status)}
            </div>
            <p className="text-sm text-muted-foreground">{checks.backendReachable.message}</p>
            {checks.backendReachable.error && (
              <pre className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 overflow-x-auto">
                {checks.backendReachable.error}
              </pre>
            )}
            {checks.backendReachable.data && (
              <pre className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs overflow-x-auto">
                {JSON.stringify(checks.backendReachable.data, null, 2)}
              </pre>
            )}
          </div>
        </div>

        {/* Check 2: AI Endpoint Exists */}
        <div className="flex items-start gap-3 p-3 border rounded-lg">
          {getStatusIcon(checks.aiEndpointExists.status)}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <h4 className="font-semibold text-sm">AI Endpoint Available</h4>
              {getStatusBadge(checks.aiEndpointExists.status)}
            </div>
            <p className="text-sm text-muted-foreground">{checks.aiEndpointExists.message}</p>
            {checks.aiEndpointExists.solution && (
              <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                <strong>Solution:</strong> {checks.aiEndpointExists.solution}
              </div>
            )}
          </div>
        </div>

        {/* Check 3: AI Configured */}
        <div className="flex items-start gap-3 p-3 border rounded-lg">
          {getStatusIcon(checks.aiConfigured.status)}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <h4 className="font-semibold text-sm">AI Configuration</h4>
              {getStatusBadge(checks.aiConfigured.status)}
            </div>
            <p className="text-sm text-muted-foreground">{checks.aiConfigured.message}</p>
            {checks.aiConfigured.solution && (
              <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-800">
                <strong>Solution:</strong> {checks.aiConfigured.solution}
              </div>
            )}
            {checks.aiConfigured.data && (
              <pre className="mt-2 p-2 bg-slate-50 border rounded text-xs overflow-x-auto">
                {JSON.stringify(checks.aiConfigured.data, null, 2)}
              </pre>
            )}
          </div>
        </div>

        {/* Check 4: Can Generate Response */}
        <div className="flex items-start gap-3 p-3 border rounded-lg">
          {getStatusIcon(checks.canGenerateResponse.status)}
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <h4 className="font-semibold text-sm">AI Response Generation</h4>
              {getStatusBadge(checks.canGenerateResponse.status)}
            </div>
            <p className="text-sm text-muted-foreground">{checks.canGenerateResponse.message}</p>
            {checks.canGenerateResponse.error && (
              <pre className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 overflow-x-auto">
                {checks.canGenerateResponse.error}
              </pre>
            )}
            {checks.canGenerateResponse.data?.message && (
              <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-xs">
                <strong>Response:</strong> {checks.canGenerateResponse.data.message.substring(0, 100)}...
              </div>
            )}
          </div>
        </div>

        {/* Configuration Info */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
          <h4 className="font-semibold mb-2 text-blue-900">Configuration</h4>
          <div className="space-y-1 text-blue-800">
            <div>Backend URL: <code className="bg-blue-100 px-1 py-0.5 rounded">{BACKEND_BASE_URL}</code></div>
            <div>API Key: <code className="bg-blue-100 px-1 py-0.5 rounded">{process.env.REACT_APP_API_KEY ? 'Configured ✓' : 'Not set ✗'}</code></div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="pt-2 border-t">
          <h4 className="font-semibold text-sm mb-2">Quick Fixes</h4>
          <ul className="text-xs space-y-1 text-muted-foreground">
            <li>• If backend is unreachable: Check REACT_APP_BACKEND_URL in frontend env</li>
            <li>• If endpoint not found: Deploy updated backend code</li>
            <li>• If AI not configured: Set GEMINI_API_KEY in backend environment</li>
            <li>• If generation fails: Check backend logs for errors</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default AIDiagnostics;
