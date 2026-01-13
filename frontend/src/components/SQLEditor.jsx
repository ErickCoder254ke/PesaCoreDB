import { useState, useRef, useEffect } from "react";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const SQL_KEYWORDS = [
  "SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "SET",
  "DELETE", "CREATE", "TABLE", "DROP", "ALTER", "JOIN", "INNER", "LEFT",
  "RIGHT", "ON", "AND", "OR", "NOT", "NULL", "TRUE", "FALSE", "PRIMARY",
  "KEY", "UNIQUE", "INT", "STRING", "BOOL", "FLOAT", "AS", "ORDER", "BY",
  "GROUP", "HAVING", "LIMIT", "OFFSET", "ASC", "DESC", "DISTINCT"
];

export function SQLEditor({ value, onChange, placeholder, className, onExecute }) {
  const textareaRef = useRef(null);
  const [highlightedContent, setHighlightedContent] = useState("");

  useEffect(() => {
    setHighlightedContent(highlightSQL(value));
  }, [value]);

  const highlightSQL = (sql) => {
    if (!sql) return "";

    let highlighted = sql;

    // Highlight SQL keywords
    SQL_KEYWORDS.forEach((keyword) => {
      const regex = new RegExp(`\\b${keyword}\\b`, "gi");
      highlighted = highlighted.replace(
        regex,
        `<span class="sql-keyword">${keyword}</span>`
      );
    });

    // Highlight strings
    highlighted = highlighted.replace(
      /'([^']*)'/g,
      '<span class="sql-string">\'$1\'</span>'
    );

    // Highlight numbers
    highlighted = highlighted.replace(
      /\b(\d+)\b/g,
      '<span class="sql-number">$1</span>'
    );

    // Highlight operators
    highlighted = highlighted.replace(
      /([=<>!]+)/g,
      '<span class="sql-operator">$1</span>'
    );

    return highlighted;
  };

  const handleKeyDown = (e) => {
    // Ctrl/Cmd + Enter to execute
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (onExecute) onExecute();
    }

    // Tab support
    if (e.key === "Tab") {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newValue = value.substring(0, start) + "  " + value.substring(end);
      onChange({ target: { value: newValue } });
      
      // Set cursor position after the tab
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 2;
      }, 0);
    }
  };

  return (
    <div className={cn("relative", className)}>
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={onChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={cn(
          "min-h-32 font-mono text-sm resize-none",
          "bg-background/50 backdrop-blur-sm",
          "focus-visible:ring-2 focus-visible:ring-primary/50",
          "transition-all duration-200"
        )}
        spellCheck={false}
      />
      <div className="absolute bottom-2 right-2 text-xs text-muted-foreground bg-background/80 px-2 py-1 rounded-md border">
        <kbd className="text-xs">Ctrl</kbd> + <kbd className="text-xs">Enter</kbd> to execute
      </div>
    </div>
  );
}

export default SQLEditor;
