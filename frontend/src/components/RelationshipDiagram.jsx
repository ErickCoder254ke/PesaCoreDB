import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { toast } from "@/components/ui/sonner";
import { Database, RefreshCw, ZoomIn, ZoomOut, Maximize2, Key, Link2, Table2, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

export function RelationshipDiagram({ currentDatabase, className }) {
  const [tables, setTables] = useState({});
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [customPositions, setCustomPositions] = useState({});
  const [draggingTable, setDraggingTable] = useState(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const svgRef = useRef(null);

  useEffect(() => {
    if (currentDatabase) {
      fetchRelationships();
      // Load custom positions from localStorage
      const savedPositions = localStorage.getItem(`diagram-positions-${currentDatabase}`);
      if (savedPositions) {
        try {
          setCustomPositions(JSON.parse(savedPositions));
        } catch (e) {
          console.error("Failed to load saved positions:", e);
        }
      }
    }
  }, [currentDatabase]);

  // Save positions to localStorage whenever they change
  useEffect(() => {
    if (currentDatabase && Object.keys(customPositions).length > 0) {
      localStorage.setItem(`diagram-positions-${currentDatabase}`, JSON.stringify(customPositions));
    }
  }, [customPositions, currentDatabase]);

  const fetchRelationships = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/relationships`, {
        params: { db: currentDatabase }
      });

      if (response.data.success) {
        setTables(response.data.tables || {});
        setRelationships(response.data.relationships || []);
      } else {
        toast.error("Failed to load relationships");
      }
    } catch (err) {
      console.error("Failed to fetch relationships:", err);
      toast.error(err.response?.data?.detail || err.message || "Failed to fetch relationships");
    } finally {
      setLoading(false);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.2, 2));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.2, 0.5));
  };

  const handleResetZoom = () => {
    setZoom(1);
  };

  const handleResetPositions = () => {
    setCustomPositions({});
    localStorage.removeItem(`diagram-positions-${currentDatabase}`);
  };

  const handleMouseDown = (tableName, x, y, event) => {
    event.stopPropagation();
    const svgRect = svgRef.current.getBoundingClientRect();
    const svgX = (event.clientX - svgRect.left) / zoom;
    const svgY = (event.clientY - svgRect.top) / zoom;

    setDraggingTable(tableName);
    setDragOffset({
      x: svgX - x,
      y: svgY - y
    });
  };

  const handleMouseMove = (event) => {
    if (!draggingTable || !svgRef.current) return;

    const svgRect = svgRef.current.getBoundingClientRect();
    const svgX = (event.clientX - svgRect.left) / zoom;
    const svgY = (event.clientY - svgRect.top) / zoom;

    const newX = svgX - dragOffset.x;
    const newY = svgY - dragOffset.y;

    setCustomPositions(prev => ({
      ...prev,
      [draggingTable]: { x: newX, y: newY }
    }));
  };

  const handleMouseUp = () => {
    setDraggingTable(null);
  };

  useEffect(() => {
    if (draggingTable) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [draggingTable, dragOffset, zoom]);

  const getTypeColor = (type) => {
    const colors = {
      INT: "bg-blue-500",
      STRING: "bg-green-500",
      BOOL: "bg-purple-500",
      FLOAT: "bg-orange-500"
    };
    return colors[type] || "bg-gray-500";
  };

  const renderDiagram = () => {
    const tableNames = Object.keys(tables);
    
    if (tableNames.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-96">
          <Database className="h-16 w-16 text-muted-foreground mb-4" />
          <p className="text-muted-foreground text-center">
            No tables found in this database.
            <br />
            Create some tables to see the relationship diagram.
          </p>
        </div>
      );
    }

    // Layout tables in a grid
    const cols = Math.ceil(Math.sqrt(tableNames.length));
    const tableWidth = 280;
    const tableSpacing = 200;
    const headerHeight = 50;
    const rowHeight = 32;
    
    const tablePositions = {};
    const tableElements = [];
    
    tableNames.forEach((tableName, index) => {
      const col = index % cols;
      const row = Math.floor(index / cols);
      const defaultX = col * (tableWidth + tableSpacing) + 50;
      const defaultY = row * 400 + 50;

      // Use custom position if available, otherwise use default grid position
      const position = customPositions[tableName] || { x: defaultX, y: defaultY };
      const x = position.x;
      const y = position.y;

      tablePositions[tableName] = { x, y };
      
      const tableData = tables[tableName];
      const columns = tableData.columns || [];
      const tableHeight = headerHeight + (columns.length * rowHeight) + 20;
      
      tableElements.push(
        <g
          key={tableName}
          className="table-group"
          style={{ cursor: draggingTable === tableName ? 'grabbing' : 'grab' }}
          onMouseDown={(e) => handleMouseDown(tableName, x, y, e)}
        >
          {/* Table container */}
          <rect
            x={x}
            y={y}
            width={tableWidth}
            height={tableHeight}
            className="fill-card stroke-primary stroke-2 hover:stroke-primary/80 transition-colors"
            rx="8"
          />
          
          {/* Table header */}
          <rect
            x={x}
            y={y}
            width={tableWidth}
            height={headerHeight}
            className="fill-primary/10 stroke-primary/20"
            rx="8"
          />
          <line
            x1={x}
            y1={y + headerHeight}
            x2={x + tableWidth}
            y2={y + headerHeight}
            className="stroke-primary/30"
            strokeWidth="2"
          />
          
          {/* Table name */}
          <text
            x={x + 15}
            y={y + headerHeight / 2 + 6}
            className="fill-foreground font-bold text-base"
          >
            <tspan className="fill-primary">📊</tspan> {tableName}
          </text>
          
          {/* Row count badge */}
          <text
            x={x + tableWidth - 15}
            y={y + headerHeight / 2 + 5}
            className="fill-muted-foreground text-xs"
            textAnchor="end"
          >
            {tableData.row_count} rows
          </text>
          
          {/* Columns */}
          {columns.map((column, colIndex) => {
            const yPos = y + headerHeight + (colIndex * rowHeight) + 10;
            
            return (
              <g key={column.name}>
                {/* Alternating row background */}
                {colIndex % 2 === 1 && (
                  <rect
                    x={x}
                    y={y + headerHeight + (colIndex * rowHeight)}
                    width={tableWidth}
                    height={rowHeight}
                    className="fill-muted/30"
                  />
                )}
                
                {/* Primary key icon */}
                {column.is_primary_key && (
                  <text x={x + 10} y={yPos + 15} className="text-sm">
                    🔑
                  </text>
                )}
                
                {/* Foreign key icon */}
                {column.foreign_key_table && (
                  <text x={x + 10} y={yPos + 15} className="text-sm">
                    🔗
                  </text>
                )}
                
                {/* Column name */}
                <text
                  x={x + (column.is_primary_key || column.foreign_key_table ? 35 : 15)}
                  y={yPos + 15}
                  className={cn(
                    "fill-foreground text-sm font-medium",
                    column.is_primary_key && "font-bold"
                  )}
                >
                  {column.name}
                </text>
                
                {/* Type badge */}
                <rect
                  x={x + tableWidth - 70}
                  y={yPos + 4}
                  width={55}
                  height={20}
                  className={cn("opacity-80", getTypeColor(column.type))}
                  rx="4"
                />
                <text
                  x={x + tableWidth - 42}
                  y={yPos + 17}
                  className="fill-white text-xs font-semibold"
                  textAnchor="middle"
                >
                  {column.type}
                </text>
              </g>
            );
          })}
        </g>
      );
    });
    
    // Draw relationship lines
    const relationshipLines = relationships.map((rel, index) => {
      const fromTable = tablePositions[rel.from_table];
      const toTable = tablePositions[rel.to_table];
      
      if (!fromTable || !toTable) return null;
      
      // Find column positions
      const fromColumns = tables[rel.from_table]?.columns || [];
      const toColumns = tables[rel.to_table]?.columns || [];
      
      const fromColIndex = fromColumns.findIndex(c => c.name === rel.from_column);
      const toColIndex = toColumns.findIndex(c => c.name === rel.to_column);
      
      // Calculate connection points
      const fromX = fromTable.x + tableWidth;
      const fromY = fromTable.y + headerHeight + (fromColIndex * rowHeight) + (rowHeight / 2);
      
      const toX = toTable.x;
      const toY = toTable.y + headerHeight + (toColIndex * rowHeight) + (rowHeight / 2);
      
      // Create curved path
      const midX = (fromX + toX) / 2;
      const path = `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`;
      
      return (
        <g key={index}>
          {/* Relationship line */}
          <path
            d={path}
            className="stroke-primary/60 fill-none hover:stroke-primary transition-colors"
            strokeWidth="2"
            strokeDasharray="5,5"
            markerEnd="url(#arrowhead)"
          />
          
          {/* Connection point at start */}
          <circle
            cx={fromX}
            cy={fromY}
            r="5"
            className="fill-primary/80 stroke-background stroke-2"
          />
          
          {/* Connection point at end */}
          <circle
            cx={toX}
            cy={toY}
            r="5"
            className="fill-primary/80 stroke-background stroke-2"
          />
          
          {/* Relationship label */}
          <text
            x={midX}
            y={(fromY + toY) / 2 - 10}
            className="fill-primary text-xs font-semibold"
            textAnchor="middle"
          >
            <tspan className="fill-background stroke-background stroke-[4px] paint-order-stroke">
              {rel.from_column} → {rel.to_column}
            </tspan>
            <tspan className="fill-primary">
              {rel.from_column} → {rel.to_column}
            </tspan>
          </text>
        </g>
      );
    });
    
    // Calculate SVG dimensions
    const maxX = Math.max(...Object.values(tablePositions).map(p => p.x)) + tableWidth + 50;
    const maxY = Math.max(...Object.values(tablePositions).map(p => p.y)) + 400;
    
    return (
      <div className="relative w-full h-full">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${maxX} ${maxY}`}
          className="w-full h-full"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }}
        >
          {/* Definitions for arrow markers */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="8"
              refY="3"
              orient="auto"
              className="fill-primary/60"
            >
              <polygon points="0 0, 10 3, 0 6" />
            </marker>
          </defs>
          
          {/* Background grid */}
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path
              d="M 50 0 L 0 0 0 50"
              fill="none"
              className="stroke-muted/20"
              strokeWidth="1"
            />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Relationship lines (drawn first, so they appear behind tables) */}
          {relationshipLines}
          
          {/* Tables */}
          {tableElements}
        </svg>
      </div>
    );
  };

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Link2 className="h-5 w-5 text-primary" />
          <span className="text-sm text-muted-foreground">
            {relationships.length} relationship{relationships.length !== 1 ? "s" : ""} 
            {" "}across {Object.keys(tables).length} table{Object.keys(tables).length !== 1 ? "s" : ""}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          {Object.keys(customPositions).length > 0 && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleResetPositions}
              className="gap-2"
            >
              <Maximize2 className="h-4 w-4" />
              Reset Layout
            </Button>
          )}

          <div className="flex items-center gap-1 border rounded-md p-1">
            <Button
              size="sm"
              variant="ghost"
              onClick={handleZoomOut}
              disabled={zoom <= 0.5}
              className="h-8 w-8 p-0"
            >
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-xs font-mono px-2 min-w-[60px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleZoomIn}
              disabled={zoom >= 2}
              className="h-8 w-8 p-0"
            >
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleResetZoom}
              className="h-8 w-8 p-0"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>

          <Button
            size="sm"
            variant="ghost"
            onClick={fetchRelationships}
            disabled={loading}
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
          </Button>
        </div>
      </div>

      {/* Legend */}
      {Object.keys(tables).length > 0 && (
        <Card className="mb-4 border-primary/20">
          <CardContent className="p-4">
            <div className="flex items-center justify-between gap-6 flex-wrap text-sm">
              <div className="flex items-center gap-6 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="text-base">🔑</span>
                  <span className="text-muted-foreground">Primary Key</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-base">🔗</span>
                  <span className="text-muted-foreground">Foreign Key</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg width="40" height="2">
                    <line x1="0" y1="1" x2="40" y2="1" className="stroke-primary/60" strokeWidth="2" strokeDasharray="5,5" />
                  </svg>
                  <span className="text-muted-foreground">Relationship</span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-xs text-muted-foreground italic">
                <span>💡 Tip: Drag tables to rearrange them</span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Diagram */}
      <Card className="flex-1 overflow-hidden border-primary/20">
        <CardContent className="p-0 h-full">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex flex-col items-center gap-4">
                <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                <p className="text-sm text-muted-foreground">Loading relationships...</p>
              </div>
            </div>
          ) : (
            <ScrollArea className="h-full w-full">
              <div className="p-6 min-w-max">
                {renderDiagram()}
              </div>
            </ScrollArea>
          )}
        </CardContent>
      </Card>

      {/* Info message */}
      {Object.keys(tables).length > 0 && relationships.length === 0 && !loading && (
        <Alert className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No relationships found. Use the <code className="bg-muted px-1 rounded">REFERENCES</code> keyword when creating tables to define foreign keys.
            <br />
            <span className="text-xs text-muted-foreground mt-1 inline-block">
              Example: <code className="bg-muted px-1 rounded">CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id))</code>
            </span>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

export default RelationshipDiagram;
