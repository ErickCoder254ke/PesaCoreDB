import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { 
  MessageCircle, 
  X, 
  Send,
  Minimize2,
  User,
  Bot,
  Loader2,
  Sparkles,
  Mail,
  MessageSquare,
  Wand2,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { generateAIResponse, validateUserQuery } from "@/lib/gemini";
import { ERICK_KNOWLEDGE_BASE, QUICK_QUESTIONS } from "@/lib/knowledge-base";
import { CONTACT_CONFIG, AI_CONFIG } from "@/lib/config";
import { chatRateLimiter, sanitizeInput, isLikelySpam, trackAIInteraction } from "@/lib/ai-utils";

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

type ChatMode = 'ai' | 'message';

// Prompt templates for users to customize
const PROMPT_TEMPLATES = [
  {
    title: "Project Inquiry",
    prompt: "I'm interested in working with Erick on a project involving [describe your project]. Could you tell me about his experience with [specific technology/skill]?"
  },
  {
    title: "Technical Skills",
    prompt: "What is Erick's level of expertise with [technology name]? Has he worked on projects using this technology?"
  },
  {
    title: "Service Details",
    prompt: "I need help with [describe your need]. Does Erick offer services in this area? What would be the typical process?"
  },
  {
    title: "Project Timeline",
    prompt: "For a [type of project] project with [brief description], how long would it typically take Erick to complete? What's his availability?"
  },
  {
    title: "Budget Discussion",
    prompt: "I have a budget of [range] for [type of project]. Can you provide information about Erick's pricing and what would be included?"
  },
  {
    title: "Custom Question",
    prompt: ""
  }
];

const ChatPopup = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [chatMode, setChatMode] = useState<ChatMode>('ai');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi! I'm Erick's AI assistant. Ask me about his skills, projects, or services. You can use quick questions or write your own custom prompts!",
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [showQuickQuestions, setShowQuickQuestions] = useState(true);
  const [useAdvancedPrompt, setUseAdvancedPrompt] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { toast } = useToast();

  // Message form state
  const [messageForm, setMessageForm] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [isSubmittingMessage, setIsSubmittingMessage] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      
      // Show popup when user scrolls to 30% of the page
      const scrollPercentage = scrollY / (documentHeight - windowHeight);
      if (scrollPercentage >= 0.3 && !isVisible) {
        setIsVisible(true);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [isVisible]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current && useAdvancedPrompt) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [inputMessage, useAdvancedPrompt]);

  const handleSendMessage = async (message?: string) => {
    const rawQuery = message || inputMessage;
    const queryText = sanitizeInput(rawQuery);
    
    // Check rate limiting
    if (!chatRateLimiter.canMakeRequest()) {
      const errorMessage: Message = {
        id: messages.length + 1,
        text: "You've reached the rate limit. Please wait a moment before asking another question.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }
    
    // Check for spam
    if (isLikelySpam(queryText)) {
      const errorMessage: Message = {
        id: messages.length + 1,
        text: "Your message appears to be invalid. Please ask a genuine question about Erick's work.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }
    
    if (!queryText.trim()) {
      toast({
        title: "Empty Message",
        description: "Please type a message before sending.",
        variant: "destructive",
      });
      return;
    }

    // Validate query
    const validation = validateUserQuery(queryText);
    if (!validation.valid) {
      toast({
        title: "Invalid Message",
        description: validation.error || "Please check your message and try again.",
        variant: "destructive",
      });
      return;
    }
    
    // Track interaction
    trackAIInteraction('user_query', { 
      query: queryText,
      isAdvancedPrompt: useAdvancedPrompt 
    });

    // Add user message
    const userMessage: Message = {
      id: messages.length + 1,
      text: queryText,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setShowQuickQuestions(false);
    setShowTemplates(false);
    setIsProcessing(true);

    // Add loading message
    const loadingMessage: Message = {
      id: messages.length + 2,
      text: "Thinking...",
      isBot: true,
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, loadingMessage]);

    try {
      // Generate AI response
      const response = await generateAIResponse(queryText, ERICK_KNOWLEDGE_BASE);

      // Remove loading message
      setMessages(prev => prev.filter(msg => !msg.isLoading));

      // Handle different response types
      let responseText = "";

      if (response.success && response.message) {
        responseText = response.message;
        trackAIInteraction('ai_response_success', { query: queryText });
      } else {
        // Handle specific error types with helpful messages
        switch (response.errorType) {
          case 'api_key':
            responseText = "⚠️ AI Configuration Issue: The API key needs to be configured. Please contact the site administrator.\n\nIn the meantime, feel free to ask questions and I'll use my knowledge base to help!";
            break;
          case 'quota':
            responseText = "⏱️ The AI service has reached its usage limit for now. Don't worry - I can still help using my built-in knowledge!\n\nTry asking me about Erick's projects, skills, or services.";
            break;
          case 'network':
            responseText = "🌐 Having trouble connecting to the AI service. This might be a temporary network issue.\n\nPlease check your connection and try again, or ask me a question and I'll use my offline knowledge base.";
            break;
          case 'safety':
            responseText = response.error || "I can only discuss Erick's professional work and skills. Please ask about his projects, technologies, or services!";
            break;
          default:
            responseText = response.error || "I encountered an issue generating a response. Try rephrasing your question or ask about Erick's skills, projects, or contact information.";
        }

        trackAIInteraction('ai_response_error', {
          query: queryText,
          errorType: response.errorType,
          error: response.error
        });
      }

      // Add AI response
      const botResponse: Message = {
        id: messages.length + 3,
        text: responseText,
        isBot: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      // Remove loading message
      setMessages(prev => prev.filter(msg => !msg.isLoading));

      console.error('Unexpected error in handleSendMessage:', error);

      // Add error message
      const errorMessage: Message = {
        id: messages.length + 3,
        text: "❌ Something unexpected happened. Please try asking another question or contact Erick directly via WhatsApp below.",
        isBot: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      trackAIInteraction('ai_response_exception', { query: queryText, error: String(error) });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question);
  };

  const handleTemplateSelect = (template: typeof PROMPT_TEMPLATES[0]) => {
    setInputMessage(template.prompt);
    setUseAdvancedPrompt(true);
    setShowTemplates(false);
    toast({
      title: "Template Loaded",
      description: "Customize the prompt and send it to the AI!",
    });
  };

  const handleContactDev = () => {
    const whatsappMessage = encodeURIComponent("Hi Erick! I found your portfolio and would like to discuss a project.");
    window.open(`${CONTACT_CONFIG.whatsappUrl}?text=${whatsappMessage}`, "_blank");
  };

  const handleSubmitCustomMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!messageForm.name.trim() || !messageForm.message.trim()) {
      toast({
        title: "Missing Information",
        description: "Please provide your name and message.",
        variant: "destructive",
      });
      return;
    }

    setIsSubmittingMessage(true);

    const data = {
      access_key: import.meta.env.VITE_WEB3FORMS_ACCESS_KEY || 'fc498626-9830-4afe-bac6-62cff94af591',
      name: messageForm.name,
      email: messageForm.email || 'no-reply@portfolio.com',
      subject: `Custom Message from ${messageForm.name} via Chat`,
      message: `
Name: ${messageForm.name}
Email: ${messageForm.email || 'Not provided'}

Message/Greeting:
${messageForm.message}

---
Sent via Portfolio Chat Widget
      `,
      from_name: messageForm.name,
      replyto: messageForm.email || 'no-reply@portfolio.com'
    };

    try {
      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        toast({
          title: "Message Sent! ✨",
          description: "Thank you for your message. Erick will get back to you soon!",
        });

        // Reset form
        setMessageForm({
          name: '',
          email: '',
          message: ''
        });

        // Track the interaction
        trackAIInteraction('custom_message_sent', { 
          hasEmail: !!messageForm.email,
          messageLength: messageForm.message.length 
        });
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again or use WhatsApp.",
        variant: "destructive",
      });
    } finally {
      setIsSubmittingMessage(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isProcessing) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <AnimatePresence>
        {isOpen && !isMinimized && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="mb-4"
          >
            <Card className="w-[340px] h-[480px] bg-card border shadow-glow flex flex-col overflow-hidden">
              {/* Header */}
              <div className="flex items-center justify-between p-3 border-b bg-gradient-to-r from-primary to-primary/90">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-primary-foreground/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                    {chatMode === 'ai' ? (
                      <Sparkles className="w-4 h-4 text-primary-foreground" />
                    ) : (
                      <Mail className="w-4 h-4 text-primary-foreground" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm text-primary-foreground">
                      {chatMode === 'ai' ? 'AI Assistant' : 'Send Message'}
                    </h3>
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse"></div>
                      <span className="text-xs text-primary-foreground/80">Online</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsMinimized(true)}
                    className="h-7 w-7 p-0 text-primary-foreground hover:bg-primary-foreground/10"
                  >
                    <Minimize2 className="h-3.5 w-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsOpen(false)}
                    className="h-7 w-7 p-0 text-primary-foreground hover:bg-primary-foreground/10"
                  >
                    <X className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* Mode Tabs */}
              <div className="flex gap-1 p-2 bg-muted/30 border-b">
                <Button
                  variant={chatMode === 'ai' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setChatMode('ai')}
                  className="flex-1 h-8 text-xs gap-1.5"
                >
                  <Bot className="w-3.5 h-3.5" />
                  AI Chat
                </Button>
                <Button
                  variant={chatMode === 'message' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setChatMode('message')}
                  className="flex-1 h-8 text-xs gap-1.5"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  Send Message
                </Button>
              </div>

              {/* AI Chat Mode */}
              {chatMode === 'ai' && (
                <>
                  {/* Messages */}
                  <ScrollArea className="flex-1 p-3">
                    <div className="space-y-3">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex gap-2 ${message.isBot ? "justify-start" : "justify-end"}`}
                        >
                          {message.isBot && (
                            <div className="w-7 h-7 bg-primary rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                              {message.isLoading ? (
                                <Loader2 className="w-3.5 h-3.5 text-primary-foreground animate-spin" />
                              ) : (
                                <Bot className="w-3.5 h-3.5 text-primary-foreground" />
                              )}
                            </div>
                          )}
                          <div
                            className={`max-w-[75%] px-3 py-2 rounded-lg text-sm leading-relaxed whitespace-pre-wrap ${
                              message.isBot
                                ? "bg-muted text-foreground rounded-tl-none"
                                : "bg-primary text-primary-foreground rounded-tr-none"
                            }`}
                          >
                            {message.text}
                          </div>
                          {!message.isBot && (
                            <div className="w-7 h-7 bg-accent rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                              <User className="w-3.5 h-3.5 text-accent-foreground" />
                            </div>
                          )}
                        </div>
                      ))}

                      {/* Quick Questions */}
                      {showQuickQuestions && messages.length === 1 && (
                        <div className="space-y-2 pt-1">
                          <p className="text-xs text-muted-foreground font-medium">Quick questions:</p>
                          <div className="flex flex-col gap-1.5">
                            {QUICK_QUESTIONS.slice(0, 3).map((question, index) => (
                              <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                onClick={() => handleQuickQuestion(question)}
                                className="text-xs h-auto py-2 px-2.5 justify-start text-left hover:bg-primary hover:text-primary-foreground transition-colors"
                                disabled={isProcessing}
                              >
                                {question}
                              </Button>
                            ))}
                          </div>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowTemplates(!showTemplates)}
                            className="w-full mt-2 text-xs gap-1.5 text-primary"
                          >
                            <Wand2 className="w-3 h-3" />
                            Or use a prompt template
                          </Button>
                        </div>
                      )}

                      {/* Prompt Templates */}
                      {showTemplates && (
                        <div className="space-y-2 pt-1">
                          <div className="flex items-center justify-between">
                            <p className="text-xs text-muted-foreground font-medium">Prompt templates:</p>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setShowTemplates(false)}
                              className="h-5 w-5 p-0"
                            >
                              <X className="w-3 h-3" />
                            </Button>
                          </div>
                          <ScrollArea className="max-h-40">
                            <div className="flex flex-col gap-1.5">
                              {PROMPT_TEMPLATES.map((template, index) => (
                                <Button
                                  key={index}
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleTemplateSelect(template)}
                                  className="text-xs h-auto py-2 px-2.5 justify-start text-left hover:bg-accent hover:text-accent-foreground transition-colors"
                                >
                                  <Wand2 className="w-3 h-3 mr-1.5 flex-shrink-0" />
                                  {template.title}
                                </Button>
                              ))}
                            </div>
                          </ScrollArea>
                        </div>
                      )}

                      <div ref={messagesEndRef} />
                    </div>
                  </ScrollArea>

                  {/* WhatsApp Button */}
                  <div className="px-3 py-2 border-t bg-muted/20">
                    <Button
                      onClick={handleContactDev}
                      size="sm"
                      variant="outline"
                      className="w-full bg-green-600 hover:bg-green-700 text-white border-green-600 gap-1.5 h-8 text-xs"
                    >
                      <MessageCircle className="w-3.5 h-3.5" />
                      Contact on WhatsApp
                    </Button>
                  </div>

                  {/* Input Area */}
                  <div className="p-3 border-t bg-background">
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        if (!isProcessing && inputMessage.trim()) {
                          handleSendMessage();
                        }
                      }}
                      className="space-y-2"
                    >
                      {/* Prompt Mode Toggle */}
                      <div className="flex items-center justify-between">
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => setUseAdvancedPrompt(!useAdvancedPrompt)}
                          className="h-6 text-[10px] gap-1 text-muted-foreground hover:text-foreground"
                        >
                          {useAdvancedPrompt ? (
                            <>
                              <ChevronUp className="w-3 h-3" />
                              Simple prompt
                            </>
                          ) : (
                            <>
                              <ChevronDown className="w-3 h-3" />
                              Advanced prompt
                            </>
                          )}
                        </Button>
                        {!showTemplates && messages.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => setShowTemplates(true)}
                            className="h-6 text-[10px] gap-1 text-muted-foreground hover:text-primary"
                          >
                            <Wand2 className="w-3 h-3" />
                            Templates
                          </Button>
                        )}
                      </div>

                      {/* Input/Textarea */}
                      <div className="flex gap-2">
                        {useAdvancedPrompt ? (
                          <Textarea
                            ref={textareaRef}
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Write your custom prompt here... (Shift+Enter for new line)"
                            disabled={isProcessing}
                            className="flex-1 px-2.5 py-1.5 text-xs border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed min-h-[32px] max-h-[100px] resize-none"
                            maxLength={AI_CONFIG.maxQueryLength}
                            rows={1}
                          />
                        ) : (
                          <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask about skills, projects..."
                            disabled={isProcessing}
                            className="flex-1 px-2.5 py-1.5 text-xs border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                            maxLength={AI_CONFIG.maxQueryLength}
                          />
                        )}
                        <Button
                          type="submit"
                          size="sm"
                          disabled={isProcessing || !inputMessage.trim()}
                          className="px-3 h-8 flex-shrink-0"
                        >
                          {isProcessing ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Send className="h-3.5 w-3.5" />
                          )}
                        </Button>
                      </div>
                      
                      <div className="flex items-center justify-between px-0.5">
                        <p className="text-[10px] text-muted-foreground">
                          Powered by Gemini AI
                        </p>
                        <p className="text-[10px] text-muted-foreground">
                          {inputMessage.length}/{AI_CONFIG.maxQueryLength}
                        </p>
                      </div>
                    </form>
                  </div>
                </>
              )}

              {/* Send Message Mode */}
              {chatMode === 'message' && (
                <ScrollArea className="flex-1 p-4">
                  <form onSubmit={handleSubmitCustomMessage} className="space-y-4">
                    <div className="space-y-1.5">
                      <p className="text-sm text-muted-foreground">
                        Send Erick a custom message or greeting! 💌
                      </p>
                    </div>

                    <div className="space-y-1.5">
                      <Label htmlFor="name" className="text-xs">
                        Your Name *
                      </Label>
                      <Input
                        id="name"
                        value={messageForm.name}
                        onChange={(e) => setMessageForm({ ...messageForm, name: e.target.value })}
                        placeholder="John Doe"
                        required
                        className="h-8 text-sm"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <Label htmlFor="email" className="text-xs">
                        Your Email (optional)
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        value={messageForm.email}
                        onChange={(e) => setMessageForm({ ...messageForm, email: e.target.value })}
                        placeholder="john@example.com"
                        className="h-8 text-sm"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <Label htmlFor="customMessage" className="text-xs">
                        Your Message or Greeting *
                      </Label>
                      <Textarea
                        id="customMessage"
                        value={messageForm.message}
                        onChange={(e) => setMessageForm({ ...messageForm, message: e.target.value })}
                        placeholder="Hey Erick! Just wanted to say..."
                        required
                        rows={5}
                        className="text-sm resize-none"
                        maxLength={1000}
                      />
                      <p className="text-[10px] text-muted-foreground">
                        {messageForm.message.length}/1000 characters
                      </p>
                    </div>

                    <Button
                      type="submit"
                      disabled={isSubmittingMessage}
                      className="w-full h-9 gap-2"
                    >
                      {isSubmittingMessage ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="h-4 w-4" />
                          Send Message
                        </>
                      )}
                    </Button>

                    <p className="text-[10px] text-muted-foreground text-center">
                      Erick will receive your message and may reach out if you provided contact info.
                    </p>
                  </form>
                </ScrollArea>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Button */}
      <AnimatePresence>
        {(!isOpen || isMinimized) && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
          >
            <Button
              onClick={() => {
                setIsOpen(true);
                setIsMinimized(false);
              }}
              size="lg"
              className="h-14 w-14 rounded-full bg-primary hover:bg-primary/90 shadow-glow relative group"
            >
              <MessageCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
              {isVisible && !isOpen && (
                <Badge className="absolute -top-1 -right-1 w-5 h-5 rounded-full p-0 bg-green-500 text-white text-[10px] flex items-center justify-center border-2 border-background">
                  AI
                </Badge>
              )}
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ChatPopup;
