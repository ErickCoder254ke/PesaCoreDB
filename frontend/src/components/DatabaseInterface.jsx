import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "@/components/ui/sonner";
import {
  Database,
  Play,
  Table,
  Trash2,
  CheckCircle,
  Zap,
  FileJson,
  History,
  Sparkles,
  Terminal,
  BarChart3,
  Layers,
  Code2,
  BookOpen,
  Hash,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { QueryHistory } from "@/components/QueryHistory";
import SchemaVisualizer from "@/components/SchemaVisualizer";
import SQLEditor from "@/components/SQLEditor";
import ExportMenu from "@/components/ExportMenu";
import DatabaseSelector from "@/components/DatabaseSelector";
import RelationshipDiagram from "@/components/RelationshipDiagram";
import SQLAssistant from "@/components/SQLAssistant";
import { cn } from "@/lib/utils";
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from "@/components/ui/resizable";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

const exampleQueries = [
  {
    title: "Create Users Table",
    category: "DDL",
    sql: "CREATE TABLE users (id INT PRIMARY KEY, email STRING UNIQUE, name STRING, is_active BOOL)",
    description: "Creates a new users table with constraints"
  },
  {
    title: "Insert User",
    category: "DML",
    sql: "INSERT INTO users VALUES (1, 'alice@example.com', 'Alice Johnson', TRUE)",
    description: "Inserts a new user record"
  },
  {
    title: "Select All Users",
    category: "DQL",
    sql: "SELECT * FROM users",
    description: "Retrieves all user records"
  },
  {
    title: "Select Active Users",
    category: "DQL",
    sql: "SELECT * FROM users WHERE is_active = TRUE",
    description: "Filters active users only"
  },
  {
    title: "Update User",
    category: "DML",
    sql: "UPDATE users SET name = 'Alice Smith' WHERE id = 1",
    description: "Updates a user's information"
  },
  {
    title: "Create Orders Table",
    category: "DDL",
    sql: "CREATE TABLE orders (order_id INT PRIMARY KEY, user_id INT, amount INT, status STRING)",
    description: "Creates an orders table"
  },
  {
    title: "Join Tables",
    category: "DQL",
    sql: "SELECT users.name, orders.amount FROM users INNER JOIN orders ON users.id = orders.user_id",
    description: "Joins users and orders"
  },
  {
    title: "Delete User",
    category: "DML",
    sql: "DELETE FROM users WHERE id = 1",
    description: "Deletes a user record"
  }
];

export default function DatabaseInterface() {
  const [currentDatabase, setCurrentDatabase] = useState(() => {
    return localStorage.getItem("current-database") || "default";
  });
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tables, setTables] = useState([]);
  const [executionTime, setExecutionTime] = useState(null);
  const [stats, setStats] = useState({ totalQueries: 0, successfulQueries: 0 });
  const [showHistory, setShowHistory] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const queryHistoryRef = useRef(null);

  // Detect screen size for responsive layout
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    fetchTables();
    loadStats();
  }, [currentDatabase]);

  const handleDatabaseChange = (newDatabase) => {
    setCurrentDatabase(newDatabase);
    localStorage.setItem("current-database", newDatabase);
    setResult(null);
  };

  const loadStats = () => {
    const savedStats = localStorage.getItem("query-stats");
    if (savedStats) setStats(JSON.parse(savedStats));
  };

  const updateStats = (success) => {
    const newStats = {
      totalQueries: stats.totalQueries + 1,
      successfulQueries: success ? stats.successfulQueries + 1 : stats.successfulQueries
    };
    setStats(newStats);
    localStorage.setItem("query-stats", JSON.stringify(newStats));
  };

  const fetchTables = async () => {
    try {
      const response = await axios.get(`${API}/tables`, {
        params: { db: currentDatabase }
      });
      setTables(response.data.tables || []);
    } catch (err) {
      console.error("Failed to fetch tables:", err);
    }
  };

  const executeQuery = async () => {
    if (!query.trim()) {
      toast.error("Please enter a SQL query");
      return;
    }

    setLoading(true);
    setResult(null);
    setExecutionTime(null);

    const startTime = performance.now();

    try {
      const response = await axios.post(`${API}/query`, {
        sql: query,
        db: currentDatabase
      });
      const endTime = performance.now();
      const execTime = Math.round(endTime - startTime);
      setExecutionTime(execTime);

      if (response.data.success) {
        toast.success(response.data.message);
        if (response.data.data) {
          setResult(response.data.data);
        }
        fetchTables();
        updateStats(true);

        if (queryHistoryRef.current) {
          queryHistoryRef.current.addToHistory(query, true, execTime);
        }
      } else {
        toast.error(response.data.error || "Query execution failed");
        updateStats(false);

        if (queryHistoryRef.current) {
          queryHistoryRef.current.addToHistory(query, false, execTime);
        }
      }
    } catch (err) {
      const endTime = performance.now();
      const execTime = Math.round(endTime - startTime);
      setExecutionTime(execTime);
      toast.error(err.response?.data?.error || err.message || "Failed to execute query");
      updateStats(false);

      if (queryHistoryRef.current) {
        queryHistoryRef.current.addToHistory(query, false, execTime);
      }
    } finally {
      setLoading(false);
    }
  };

  const initializeDemoData = async () => {
    setLoading(true);

    try {
      const response = await axios.post(`${API}/initialize-demo`, null, {
        params: { db: currentDatabase }
      });
      toast.success(response.data.message);
      fetchTables();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to initialize demo data");
    } finally {
      setLoading(false);
    }
  };

  const dropTable = async (tableName) => {
    if (!window.confirm(`Are you sure you want to drop table '${tableName}'?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/tables/${tableName}`, {
        params: { db: currentDatabase }
      });
      toast.success(`Table '${tableName}' dropped successfully`);
      fetchTables();
      setResult(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to drop table");
    }
  };

  const handleSelectQuery = (selectedQuery) => {
    setQuery(selectedQuery);
  };

  const renderTable = (data) => {
    if (!data || data.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-12">
          <FileJson className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground text-sm">No data to display</p>
        </div>
      );
    }

    const columns = Object.keys(data[0]);

    return (
      <div className="rounded-lg border border-border overflow-hidden bg-card">
        <div className="overflow-auto max-h-[500px]">
          <table className="w-full border-collapse">
            <thead className="sticky top-0 z-10">
              <tr className="bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10 border-b-2 border-primary/20">
                <th className="px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-muted-foreground border-r border-border/50 bg-muted/50">
                  <div className="flex items-center gap-2">
                    <Hash className="h-3 w-3" />
                    #
                  </div>
                </th>
                {columns.map((col, idx) => (
                  <th 
                    key={col} 
                    className={cn(
                      "px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-muted-foreground",
                      idx < columns.length - 1 && "border-r border-border/50"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <span className="truncate">{col}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {data.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className={cn(
                    "transition-all duration-200 group",
                    "hover:bg-primary/5 hover:shadow-sm",
                    rowIdx % 2 === 0 ? "bg-background" : "bg-muted/30",
                    "animate-in fade-in slide-in-from-bottom-1"
                  )}
                  style={{ animationDelay: `${rowIdx * 20}ms` }}
                >
                  <td className="px-4 py-3 text-sm border-r border-border/50 bg-muted/40 font-mono text-muted-foreground">
                    <div className="flex items-center justify-center">
                      <Badge variant="outline" className="text-xs font-mono">
                        {rowIdx + 1}
                      </Badge>
                    </div>
                  </td>
                  {columns.map((col, colIdx) => {
                    const value = row[col];
                    const isBoolean = typeof value === 'boolean';
                    const isNumber = typeof value === 'number';
                    const isNull = value === null || value === undefined;
                    
                    return (
                      <td 
                        key={col} 
                        className={cn(
                          "px-4 py-3 text-sm",
                          colIdx < columns.length - 1 && "border-r border-border/50"
                        )}
                      >
                        {isNull ? (
                          <span className="text-muted-foreground italic text-xs">NULL</span>
                        ) : isBoolean ? (
                          <Badge 
                            variant={value ? "default" : "secondary"}
                            className={cn(
                              "text-xs font-semibold",
                              value 
                                ? "bg-green-500/90 hover:bg-green-500 text-white" 
                                : "bg-gray-500/90 hover:bg-gray-500 text-white"
                            )}
                          >
                            {value ? "TRUE" : "FALSE"}
                          </Badge>
                        ) : isNumber ? (
                          <span className="font-mono text-blue-600 dark:text-blue-400 font-medium">
                            {value.toLocaleString()}
                          </span>
                        ) : (
                          <span className="text-foreground">{String(value)}</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Table Footer with Stats */}
        <div className="border-t border-border bg-muted/30 px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              {data.length} row{data.length !== 1 ? 's' : ''}
            </span>
            <span className="flex items-center gap-1">
              <Table className="h-3 w-3" />
              {columns.length} column{columns.length !== 1 ? 's' : ''}
            </span>
          </div>
          <ExportMenu data={data} disabled={!data || data.length === 0} />
        </div>
      </div>
    );
  };

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
        <div className="max-w-[1920px] mx-auto p-4 md:p-6 lg:p-8 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between animate-in fade-in slide-in-from-top-4 duration-700">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Database className="h-10 w-10 md:h-12 md:w-12 text-primary animate-in zoom-in duration-500" />
                <Sparkles className="h-4 w-4 md:h-5 md:w-5 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl md:text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                  PesacodeDB
                </h1>
                <p className="text-xs md:text-sm text-muted-foreground">
                  Relational Database Management System
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={initializeDemoData}
                    disabled={loading}
                    variant="secondary"
                    className="gap-2 transition-all hover:scale-105"
                  >
                    <Zap className="h-4 w-4" />
                    <span className="hidden sm:inline">Demo Data</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Initialize with sample users and orders</p>
                </TooltipContent>
              </Tooltip>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowHistory(!showHistory)}
                className={cn(
                  "transition-all",
                  showHistory && "bg-primary/10 text-primary"
                )}
              >
                <History className="h-5 w-5" />
              </Button>
              <ThemeToggle />
            </div>
          </div>

          {/* Database Selector */}
          <Card className="animate-in fade-in slide-in-from-top-4 duration-700 delay-100 border-primary/20">
            <CardContent className="p-4">
              <DatabaseSelector
                currentDatabase={currentDatabase}
                onDatabaseChange={handleDatabaseChange}
              />
            </CardContent>
          </Card>

          {/* Stats Bar */}
          <Card className="animate-in fade-in slide-in-from-top-4 duration-700 delay-150 border-primary/20">
            <CardContent className="p-4">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4 md:gap-8 flex-wrap">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-xs text-muted-foreground">Total Queries</p>
                      <p className="text-xl md:text-2xl font-bold">{stats.totalQueries}</p>
                    </div>
                  </div>
                  <Separator orientation="vertical" className="h-12 hidden md:block" />
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <div>
                      <p className="text-xs text-muted-foreground">Successful</p>
                      <p className="text-xl md:text-2xl font-bold text-green-600 dark:text-green-400">
                        {stats.successfulQueries}
                      </p>
                    </div>
                  </div>
                  <Separator orientation="vertical" className="h-12 hidden md:block" />
                  <div className="flex items-center gap-2">
                    <Table className="h-5 w-5 text-blue-500" />
                    <div>
                      <p className="text-xs text-muted-foreground">Tables</p>
                      <p className="text-xl md:text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {tables.length}
                      </p>
                    </div>
                  </div>
                </div>
                {executionTime !== null && (
                  <Badge variant="outline" className="gap-2 px-4 py-2">
                    <Terminal className="h-4 w-4" />
                    Last query: {executionTime}ms
                  </Badge>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Main Content - Resizable 3 Column Layout: SQL Editor, AI Assistant, Query Templates */}
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200 h-[800px] lg:h-[600px]">
            <ResizablePanelGroup
              direction={isMobile ? "vertical" : "horizontal"}
              className="rounded-lg border border-primary/20 shadow-lg bg-card overflow-hidden"
            >
              {/* Panel 1: SQL Editor */}
              <ResizablePanel defaultSize={isMobile ? 40 : 50} minSize={isMobile ? 25 : 30}>
                <Card className="border-none shadow-none h-full flex flex-col rounded-none">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Code2 className="h-5 w-5 text-primary" />
                      SQL Editor
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Write and execute your SQL queries
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col gap-4 overflow-hidden">
                    <div className="flex-1 overflow-hidden">
                      <SQLEditor
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Enter SQL query (e.g., SELECT * FROM users)&#10;&#10;Shortcuts:&#10;• Ctrl/Cmd + Enter to execute&#10;• Tab for indentation"
                        onExecute={executeQuery}
                        className="h-full"
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={executeQuery}
                        disabled={loading}
                        className="flex-1 gap-2 transition-all hover:scale-105"
                        size="lg"
                      >
                        {loading ? (
                          <>
                            <div className="h-4 w-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                            Executing...
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4" />
                            Execute Query
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setQuery("")}
                        disabled={!query}
                      >
                        Clear
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </ResizablePanel>

              <ResizableHandle withHandle />

              {/* Panel 2: AI Assistant */}
              <ResizablePanel defaultSize={isMobile ? 30 : 25} minSize={isMobile ? 20 : 20}>
                <div className="h-full p-4">
                  <SQLAssistant
                    tables={tables}
                    onInsertQuery={handleSelectQuery}
                    currentDatabase={currentDatabase}
                    className="h-full border-none shadow-none"
                  />
                </div>
              </ResizablePanel>

              <ResizableHandle withHandle />

              {/* Panel 3: Query Templates or History */}
              <ResizablePanel defaultSize={isMobile ? 30 : 25} minSize={isMobile ? 20 : 20}>
                {showHistory ? (
                  <div className="h-full p-4">
                    <QueryHistory
                      ref={queryHistoryRef}
                      onSelectQuery={handleSelectQuery}
                      className="h-full border-none shadow-none"
                    />
                  </div>
                ) : (
                  <Card className="border-none shadow-none h-full flex flex-col rounded-none">
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <BookOpen className="h-5 w-5 text-primary" />
                        Query Templates
                      </CardTitle>
                      <CardDescription className="text-xs">
                        Click any template to load into the editor
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-hidden p-0">
                      <Tabs defaultValue="all" className="w-full h-full flex flex-col">
                        <TabsList className="grid w-full grid-cols-4 mx-4">
                          <TabsTrigger value="all" className="text-xs">All</TabsTrigger>
                          <TabsTrigger value="DQL" className="text-xs">DQL</TabsTrigger>
                          <TabsTrigger value="DML" className="text-xs">DML</TabsTrigger>
                          <TabsTrigger value="DDL" className="text-xs">DDL</TabsTrigger>
                        </TabsList>
                        {["all", "DQL", "DML", "DDL"].map((category) => (
                          <TabsContent key={category} value={category} className="flex-1 overflow-hidden mt-2 px-4 pb-4">
                            <ScrollArea className="h-full">
                              <div className="space-y-2 pr-4">
                                {exampleQueries
                                  .filter((ex) => category === "all" || ex.category === category)
                                  .map((example, idx) => (
                                    <Card
                                      key={idx}
                                      className="cursor-pointer transition-all hover:border-primary/50 hover:shadow-md hover:scale-[1.02]"
                                      onClick={() => setQuery(example.sql)}
                                    >
                                      <CardContent className="p-3">
                                        <div className="flex items-start justify-between gap-2 mb-2">
                                          <h4 className="font-semibold text-xs">{example.title}</h4>
                                          <Badge variant="outline" className="text-xs">
                                            {example.category}
                                          </Badge>
                                        </div>
                                        <p className="text-xs text-muted-foreground mb-2">
                                          {example.description}
                                        </p>
                                        <code className="text-xs block bg-muted p-2 rounded-md font-mono line-clamp-2">
                                          {example.sql}
                                        </code>
                                      </CardContent>
                                    </Card>
                                  ))}
                              </div>
                            </ScrollArea>
                          </TabsContent>
                        ))}
                      </Tabs>
                    </CardContent>
                  </Card>
                )}
              </ResizablePanel>
            </ResizablePanelGroup>
          </div>

          {/* Query Results - Full Width */}
          {result && (
            <Card className="animate-in fade-in slide-in-from-bottom-4 border-primary/20 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Layers className="h-5 w-5 text-primary" />
                  Query Results
                </CardTitle>
                <CardDescription className="text-xs">
                  Displaying {result.length} row{result.length !== 1 ? 's' : ''}
                  {executionTime && ` • Executed in ${executionTime}ms`}
                </CardDescription>
              </CardHeader>
              <CardContent>{renderTable(result)}</CardContent>
            </Card>
          )}

          {/* Database Explorer - Schema and Relationships */}
          <Card className="border-primary/20 shadow-lg animate-in fade-in slide-in-from-bottom-4 duration-700">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Database className="h-5 w-5 text-primary" />
                    Database Explorer
                  </CardTitle>
                  <CardDescription className="text-xs mt-1">
                    Visual representation of tables, columns, and relationships
                  </CardDescription>
                </div>
                <Badge variant="outline" className="gap-2">
                  <Table className="h-3 w-3" />
                  {tables.length} {tables.length === 1 ? 'table' : 'tables'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="schema" className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="schema" className="gap-2">
                    <Layers className="h-4 w-4" />
                    Schema
                  </TabsTrigger>
                  <TabsTrigger value="relationships" className="gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Relationships
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="schema" className="mt-4">
                  <SchemaVisualizer
                    currentDatabase={currentDatabase}
                    onGenerateQuery={handleSelectQuery}
                  />
                </TabsContent>
                <TabsContent value="relationships" className="mt-4">
                  <div className="h-[600px]">
                    <RelationshipDiagram currentDatabase={currentDatabase} />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </div>
    </TooltipProvider>
  );
}
