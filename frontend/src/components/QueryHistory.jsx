import { useState, useEffect, forwardRef, useImperativeHandle } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Clock, Search, Trash2, Star, Play } from "lucide-react";
import { cn } from "@/lib/utils";

export const QueryHistory = forwardRef(({ onSelectQuery, className }, ref) => {
  const [history, setHistory] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const savedHistory = localStorage.getItem("query-history");
    const savedFavorites = localStorage.getItem("query-favorites");
    if (savedHistory) setHistory(JSON.parse(savedHistory));
    if (savedFavorites) setFavorites(JSON.parse(savedFavorites));
  }, []);

  const addToHistory = (query, success, executionTime) => {
    const newEntry = {
      id: Date.now(),
      query,
      timestamp: new Date().toISOString(),
      success,
      executionTime
    };
    
    const newHistory = [newEntry, ...history].slice(0, 50); // Keep last 50 queries
    setHistory(newHistory);
    localStorage.setItem("query-history", JSON.stringify(newHistory));
  };

  const toggleFavorite = (query) => {
    const isFavorite = favorites.some(fav => fav.query === query);
    let newFavorites;
    
    if (isFavorite) {
      newFavorites = favorites.filter(fav => fav.query !== query);
    } else {
      newFavorites = [...favorites, { id: Date.now(), query }];
    }
    
    setFavorites(newFavorites);
    localStorage.setItem("query-favorites", JSON.stringify(newFavorites));
  };

  const clearHistory = () => {
    if (window.confirm("Are you sure you want to clear all history?")) {
      setHistory([]);
      localStorage.removeItem("query-history");
    }
  };

  const filteredHistory = history.filter(entry =>
    entry.query.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isFavorite = (query) => favorites.some(fav => fav.query === query);

  // Expose addToHistory to parent component
  useImperativeHandle(ref, () => ({
    addToHistory
  }));

  return (
    <Card className={cn("h-full flex flex-col", className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Query History
            </CardTitle>
            <CardDescription>
              {history.length} queries in history
            </CardDescription>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={clearHistory}
            disabled={history.length === 0}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col space-y-4 overflow-hidden">
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search queries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>

        {favorites.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
              <Star className="h-4 w-4 fill-yellow-500 text-yellow-500" />
              Favorites
            </h4>
            <div className="space-y-2">
              {favorites.map((fav) => (
                <div
                  key={fav.id}
                  className="group relative p-3 bg-muted/50 rounded-lg border border-border/50 hover:border-primary/50 transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-2">
                    <code className="text-xs flex-1 line-clamp-2">{fav.query}</code>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={() => onSelectQuery(fav.query)}
                      >
                        <Play className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0"
                        onClick={() => toggleFavorite(fav.query)}
                      >
                        <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex-1 overflow-hidden">
          <h4 className="text-sm font-semibold text-muted-foreground mb-2">Recent</h4>
          <ScrollArea className="h-full pr-4">
            <div className="space-y-2">
              {filteredHistory.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  {searchTerm ? "No queries found" : "No queries yet"}
                </p>
              ) : (
                filteredHistory.map((entry) => (
                  <div
                    key={entry.id}
                    className="group relative p-3 bg-card rounded-lg border border-border hover:border-primary/50 transition-all cursor-pointer"
                    onClick={() => onSelectQuery(entry.query)}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <Badge
                        variant={entry.success ? "default" : "destructive"}
                        className="text-xs"
                      >
                        {entry.success ? "Success" : "Failed"}
                      </Badge>
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6 p-0"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleFavorite(entry.query);
                          }}
                        >
                          <Star
                            className={cn(
                              "h-3 w-3",
                              isFavorite(entry.query) && "fill-yellow-500 text-yellow-500"
                            )}
                          />
                        </Button>
                      </div>
                    </div>
                    <code className="text-xs block mb-2 line-clamp-2">{entry.query}</code>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      {new Date(entry.timestamp).toLocaleTimeString()}
                      {entry.executionTime && (
                        <span className="ml-auto">{entry.executionTime}ms</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
});

QueryHistory.displayName = "QueryHistory";

export default QueryHistory;
