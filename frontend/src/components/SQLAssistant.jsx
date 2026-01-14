import { useState, useEffect, useRef } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "@/components/ui/sonner";
import {
  Bot,
  Send,
  Sparkles,
  Loader2,
  Copy,
  Check,
  Code2,
  Lightbulb,
  Zap,
  BookOpen,
  MessageSquare,
  X,
} from "lucide-react";
import { 
  generateSQLFromNaturalLanguage, 
  explainSQLQuery,
  optimizeSQLQuery 
} from "@/lib/gemini";
import { 
  SQL_KNOWLEDGE_BASE, 
  QUICK_SQL_QUESTIONS,
  buildSchemaContext 
} from "@/lib/sql-knowledge-base";
import { chatRateLimiter, sanitizeInput } from "@/lib/ai-utils";
import { cn } from "@/lib/utils";

const SQLAssistant = ({ tables = [], onInsertQuery, currentDatabase = "default", className }) => {
  const [userInput, setUserInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [aiConfigured, setAiConfigured] = useState(null); // null = checking, true/false = result
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content: "👋 Hi! I'm your SQL Assistant. Ask me to write queries, explain SQL, or optimize your database operations!",
      timestamp: new Date(),
    },
  ]);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check AI configuration on mount
  useEffect(() => {
    const checkAI = async () => {
      try {
        const { checkAIConfiguration } = await import('@/lib/gemini');
        const config = await checkAIConfiguration();
        console.log('🤖 AI Configuration Check:', config);
        setAiConfigured(config.enabled);

        if (!config.enabled) {
          console.warn('⚠️ AI is not configured:', config.message);
        }
      } catch (error) {
        console.error('❌ Failed to check AI configuration:', error);
        setAiConfigured(false);
      }
    };

    checkAI();
  }, []);

  const schemaContext = buildSchemaContext(tables);

  const addMessage = (role, content) => {
    const newMessage = {
      id: Date.now(),
      role,
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  };

  const handleSendMessage = async () => {
    const sanitized = sanitizeInput(userInput);

    if (!sanitized.trim()) {
      toast.error("Please enter a message");
      return;
    }

    if (!chatRateLimiter.canMakeRequest()) {
      toast.error("Too many requests. Please wait a moment.");
      return;
    }

    addMessage("user", sanitized);
    setUserInput("");
    setIsProcessing(true);

    const loadingMsg = addMessage("assistant", "🤔 Thinking...");

    try {
      const fullContext = `${SQL_KNOWLEDGE_BASE}\n\n${schemaContext}`;
      let response;

      // Detect if user wants to explain a query
      const explainMatch = sanitized.match(/^explain:?\s*(.+)/i);
      if (explainMatch) {
        const queryToExplain = explainMatch[1].trim();
        response = await explainSQLQuery(queryToExplain, fullContext);
      }
      // Detect if user wants to optimize a query
      else if (sanitized.match(/^optimize:?\s*/i)) {
        const optimizeMatch = sanitized.match(/^optimize:?\s*(.+)/i);
        const queryToOptimize = optimizeMatch[1].trim();
        response = await optimizeSQLQuery(queryToOptimize, fullContext);
      }
      // Default: Generate SQL from natural language
      else {
        response = await generateSQLFromNaturalLanguage(sanitized, fullContext);
      }

      setMessages((prev) => prev.filter((msg) => msg.id !== loadingMsg.id));

      if (response.success) {
        addMessage("assistant", response.message);
      } else {
        const errorMsg = getErrorMessage(response);
        addMessage("assistant", errorMsg);
      }
    } catch (error) {
      setMessages((prev) => prev.filter((msg) => msg.id !== loadingMsg.id));
      addMessage("assistant", "❌ Sorry, I encountered an error. Please try again.");
      console.error("SQL Assistant Error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleQuickQuestion = (question) => {
    setUserInput(question);
  };

  const copyToClipboard = (text, id) => {
    const sqlMatch = text.match(/```sql\n([\s\S]*?)\n```/);
    const textToCopy = sqlMatch ? sqlMatch[1] : text;

    navigator.clipboard.writeText(textToCopy);
    setCopiedId(id);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const insertQueryIntoEditor = (text) => {
    const sqlMatch = text.match(/```sql\n([\s\S]*?)\n```/);
    const query = sqlMatch ? sqlMatch[1] : text;

    if (onInsertQuery) {
      onInsertQuery(query);
      toast.success("Query inserted into editor!");
    }
  };

  const getErrorMessage = (response) => {
    switch (response.errorType) {
      case "api_key":
        return "⚠️ AI is not configured on the backend.\n\n" +
               "Administrator: Set the GEMINI_API_KEY environment variable on your backend server.\n\n" +
               "You can still use the SQL templates in the middle panel!";
      case "quota":
        return "⏱️ API rate limit reached. Please wait a moment and try again.";
      case "network":
        return "🌐 Network error. Could not connect to backend.\n\n" +
               "Please check:\n" +
               "• Backend server is running\n" +
               "• REACT_APP_BACKEND_URL is configured correctly\n" +
               "• No CORS issues in browser console";
      case "auth":
        return "🔒 Authentication failed.\n\n" +
               "Check that your API key is configured correctly.";
      case "safety":
        return "⚠️ Your request was blocked for safety reasons. Please rephrase your question.";
      default:
        return `❌ ${response.error || "Something went wrong. Please try again."}`;
    }
  };

  const renderMessage = (message) => {
    const isUser = message.role === "user";
    const hasSQLCode = message.content.includes("```sql");

    return (
      <div
        key={message.id}
        className={cn(
          "flex gap-2 animate-in fade-in slide-in-from-bottom-2",
          isUser ? "justify-end" : "justify-start"
        )}
      >
        {!isUser && (
          <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Bot className="w-3.5 h-3.5 text-primary" />
          </div>
        )}
        <div
          className={cn(
            "max-w-[85%] rounded-lg px-3 py-2 text-xs",
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-foreground"
          )}
        >
          <div className="whitespace-pre-wrap break-words">
            {formatMessageContent(message.content)}
          </div>
          {!isUser && hasSQLCode && (
            <div className="flex gap-1.5 mt-2 pt-2 border-t border-border/40">
              <Button
                size="sm"
                variant="ghost"
                className="h-6 text-[10px] gap-1 px-2"
                onClick={() => copyToClipboard(message.content, message.id)}
              >
                {copiedId === message.id ? (
                  <>
                    <Check className="w-3 h-3" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    Copy
                  </>
                )}
              </Button>
              {onInsertQuery && (
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 text-[10px] gap-1 px-2"
                  onClick={() => insertQueryIntoEditor(message.content)}
                >
                  <Code2 className="w-3 h-3" />
                  Insert
                </Button>
              )}
            </div>
          )}
        </div>
        {isUser && (
          <div className="w-7 h-7 rounded-full bg-accent flex items-center justify-center flex-shrink-0">
            <MessageSquare className="w-3.5 h-3.5 text-accent-foreground" />
          </div>
        )}
      </div>
    );
  };

  const formatMessageContent = (content) => {
    const parts = content.split(/(```sql[\s\S]*?```|```[\s\S]*?```|\*\*.*?\*\*)/);
    
    return parts.map((part, idx) => {
      if (part.startsWith("```sql")) {
        const code = part.replace(/```sql\n?/, "").replace(/\n?```$/, "");
        return (
          <pre key={idx} className="bg-background/50 p-2 rounded my-1.5 overflow-x-auto">
            <code className="text-[11px] font-mono text-blue-600 dark:text-blue-400">{code}</code>
          </pre>
        );
      } else if (part.startsWith("```")) {
        const code = part.replace(/```\n?/, "").replace(/\n?```$/, "");
        return (
          <pre key={idx} className="bg-background/50 p-2 rounded my-1.5 overflow-x-auto">
            <code className="text-[11px] font-mono">{code}</code>
          </pre>
        );
      } else if (part.startsWith("**") && part.endsWith("**")) {
        const text = part.replace(/\*\*/g, "");
        return (
          <strong key={idx} className="font-semibold">
            {text}
          </strong>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  };

  return (
    <Card className={cn("border-primary/20 shadow-lg h-full flex flex-col", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-4 h-4 text-primary-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg flex items-center gap-2">
              AI Assistant
              <Badge variant="secondary" className="text-[10px] gap-1 px-1.5 py-0">
                <Bot className="w-2.5 h-2.5" />
                Gemini
              </Badge>
            </CardTitle>
            <CardDescription className="text-xs">
              Natural language to SQL
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col gap-3 overflow-hidden p-4 pt-0">
        {/* Chat Messages */}
        <ScrollArea className="flex-1 -mx-4 px-4">
          <div className="space-y-3">
            {messages.map((msg) => renderMessage(msg))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Quick Questions */}
        {messages.length <= 2 && (
          <div className="space-y-2">
            <p className="text-[10px] text-muted-foreground font-medium">
              Quick questions:
            </p>
            <div className="flex flex-col gap-1.5">
              {QUICK_SQL_QUESTIONS.slice(0, 3).map((question, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => handleQuickQuestion(question)}
                  className="text-[10px] h-auto py-1.5 px-2 justify-start text-left hover:bg-primary hover:text-primary-foreground"
                  disabled={isProcessing}
                >
                  {question}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="space-y-2 border-t pt-3">
          <Textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Ask me to write, explain, or optimize SQL..."
            className="min-h-[60px] text-xs resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                if (!isProcessing && userInput.trim()) {
                  handleSendMessage();
                }
              }
            }}
            disabled={isProcessing}
          />
          <div className="flex gap-1.5">
            <Button
              onClick={handleSendMessage}
              disabled={isProcessing || !userInput.trim()}
              className="flex-1 gap-1.5 h-8 text-xs"
              size="sm"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="h-3 w-3" />
                  Send
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-1.5 border-t pt-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-1 text-[10px] h-7"
                  onClick={() => setUserInput("Write a query to ")}
                >
                  <Lightbulb className="h-3 w-3" />
                  Generate
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Generate SQL query</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-1 text-[10px] h-7"
                  onClick={() => setUserInput("Explain: ")}
                >
                  <BookOpen className="h-3 w-3" />
                  Explain
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Explain a query</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-1 text-[10px] h-7"
                  onClick={() => setUserInput("Optimize: ")}
                >
                  <Zap className="h-3 w-3" />
                  Optimize
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Optimize a query</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardContent>
    </Card>
  );
};

export default SQLAssistant;
