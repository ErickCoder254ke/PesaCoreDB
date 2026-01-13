import { useState, useEffect } from "react";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Database, Table2, Key, Link2, RefreshCw, Eye, Layers, Hash, FileJson } from "lucide-react";
import { cn } from "@/lib/utils";
import ExportMenu from "@/components/ExportMenu";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

export function SchemaVisualizer({ onGenerateQuery, className }) {
  const [tables, setTables] = useState([]);
  const [tableDetails, setTableDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [expandedTables, setExpandedTables] = useState([]);
  
  // Table data viewing
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [dataError, setDataError] = useState(null);

  useEffect(() => {
    fetchSchema();
  }, []);

  const fetchSchema = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/tables`);
      const tableNames = response.data.tables || [];
      setTables(tableNames);

      // Fetch details for each table
      const details = {};
      for (const tableName of tableNames) {
        try {
          const detailResponse = await axios.get(`${API}/tables/${tableName}`);
          details[tableName] = detailResponse.data;
        } catch (err) {
          console.error(`Failed to fetch details for ${tableName}:`, err);
        }
      }
      setTableDetails(details);
    } catch (err) {
      console.error("Failed to fetch schema:", err);
    } finally {
      setLoading(false);
    }
  };

  const viewTableData = async (tableName) => {
    setSelectedTable(tableName);
    setLoadingData(true);
    setDataError(null);
    setTableData([]);

    try {
      const response = await axios.post(`${API}/query`, {
        sql: `SELECT * FROM ${tableName}`
      });

      if (response.data.success && response.data.data) {
        setTableData(response.data.data);
      } else {
        setDataError(response.data.error || "Failed to load table data");
      }
    } catch (err) {
      setDataError(err.response?.data?.error || err.message || "Failed to fetch table data");
    } finally {
      setLoadingData(false);
    }
  };

  const generateSelectQuery = (tableName) => {
    onGenerateQuery(`SELECT * FROM ${tableName}`);
  };

  const generateInsertQuery = (tableName) => {
    const details = tableDetails[tableName];
    if (!details) return;

    const columns = details.columns.map(col => col.name).join(", ");
    const placeholders = details.columns.map(() => "?").join(", ");
    onGenerateQuery(`INSERT INTO ${tableName} (${columns}) VALUES (${placeholders})`);
  };

  const getTypeColor = (type) => {
    const colors = {
      INT: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
      STRING: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
      BOOL: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
      FLOAT: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300"
    };
    return colors[type] || "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
  };

  const renderTableDataView = () => {
    if (loadingData) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-4">
            <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-muted-foreground">Loading table data...</p>
          </div>
        </div>
      );
    }

    if (dataError) {
      return (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <FileJson className="h-12 w-12 text-destructive mb-4" />
          <p className="text-sm text-destructive">{dataError}</p>
        </div>
      );
    }

    if (!tableData || tableData.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-12">
          <FileJson className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground text-sm">No data in this table</p>
        </div>
      );
    }

    const columns = Object.keys(tableData[0]);

    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-border overflow-hidden bg-card">
          <ScrollArea className="h-[500px]">
            <Table>
              <TableHeader className="sticky top-0 z-10 bg-muted/95 backdrop-blur">
                <TableRow className="border-b-2 border-primary/20 hover:bg-muted/95">
                  <TableHead className="w-[60px] font-bold text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Hash className="h-3 w-3" />
                      #
                    </div>
                  </TableHead>
                  {columns.map((col) => (
                    <TableHead key={col} className="font-bold text-muted-foreground">
                      <div className="flex items-center gap-2">
                        <span className="truncate uppercase text-xs">{col}</span>
                      </div>
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {tableData.map((row, rowIdx) => (
                  <TableRow
                    key={rowIdx}
                    className={cn(
                      "transition-all duration-200 hover:bg-primary/5",
                      rowIdx % 2 === 0 ? "bg-background" : "bg-muted/30"
                    )}
                  >
                    <TableCell className="font-mono text-muted-foreground text-center">
                      <Badge variant="outline" className="text-xs">
                        {rowIdx + 1}
                      </Badge>
                    </TableCell>
                    {columns.map((col) => {
                      const value = row[col];
                      const isBoolean = typeof value === 'boolean';
                      const isNumber = typeof value === 'number';
                      const isNull = value === null || value === undefined;

                      return (
                        <TableCell key={col}>
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
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </ScrollArea>
        </div>

        {/* Table Footer with Stats */}
        <div className="flex items-center justify-between px-4 py-2 bg-muted/30 rounded-lg border border-border">
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              {tableData.length} row{tableData.length !== 1 ? 's' : ''}
            </span>
            <span className="flex items-center gap-1">
              <Table2 className="h-3 w-3" />
              {columns.length} column{columns.length !== 1 ? 's' : ''}
            </span>
          </div>
          <ExportMenu data={tableData} disabled={!tableData || tableData.length === 0} />
        </div>
      </div>
    );
  };

  return (
    <>
      <div className={cn("h-full flex flex-col", className)}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            <span className="text-sm text-muted-foreground">
              {tables.length} table{tables.length !== 1 ? "s" : ""} in database
            </span>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={fetchSchema}
            disabled={loading}
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
          </Button>
        </div>

        <ScrollArea className="flex-1 pr-4">
          {tables.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Database className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground">
                No tables yet. Create your first table to get started.
              </p>
            </div>
          ) : (
            <Accordion type="multiple" value={expandedTables} onValueChange={setExpandedTables}>
              {tables.map((tableName) => {
                const details = tableDetails[tableName];
                return (
                  <AccordionItem key={tableName} value={tableName} className="border rounded-lg mb-3 px-4 hover:border-primary/50 transition-colors">
                    <AccordionTrigger className="hover:no-underline">
                      <div className="flex items-center gap-2">
                        <Table2 className="h-4 w-4 text-primary" />
                        <span className="font-mono font-semibold">{tableName}</span>
                        {details && (
                          <Badge variant="secondary" className="ml-2">
                            {details.row_count} rows
                          </Badge>
                        )}
                      </div>
                    </AccordionTrigger>
                    <AccordionContent className="space-y-4 pt-2">
                      {details ? (
                        <>
                          {/* View Table Data Button */}
                          <Button
                            onClick={() => viewTableData(tableName)}
                            className="w-full gap-2"
                            variant="default"
                          >
                            <Eye className="h-4 w-4" />
                            View Table Data
                          </Button>

                          <Separator />

                          <div className="space-y-2">
                            <h4 className="text-sm font-semibold text-muted-foreground">Columns</h4>
                            <div className="space-y-1">
                              {details.columns.map((column) => (
                                <div
                                  key={column.name}
                                  className="flex items-center justify-between p-2 bg-muted/50 rounded-md"
                                >
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-sm">{column.name}</span>
                                    {column.is_primary_key && (
                                      <Badge variant="default" className="text-xs gap-1">
                                        <Key className="h-3 w-3" />
                                        PK
                                      </Badge>
                                    )}
                                    {column.is_unique && !column.is_primary_key && (
                                      <Badge variant="outline" className="text-xs">
                                        UNIQUE
                                      </Badge>
                                    )}
                                  </div>
                                  <Badge className={cn("text-xs", getTypeColor(column.type))}>
                                    {column.type}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>

                          {details.indexes && details.indexes.length > 0 && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
                                <Link2 className="h-4 w-4" />
                                Indexes
                              </h4>
                              <div className="space-y-1">
                                {details.indexes.map((index) => (
                                  <div key={index} className="text-xs font-mono p-2 bg-muted/50 rounded-md">
                                    {index}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <Separator />

                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => generateSelectQuery(tableName)}
                              className="flex-1"
                            >
                              <Eye className="h-3 w-3 mr-1" />
                              SELECT
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => generateInsertQuery(tableName)}
                              className="flex-1"
                            >
                              INSERT
                            </Button>
                          </div>
                        </>
                      ) : (
                        <p className="text-sm text-muted-foreground">Loading details...</p>
                      )}
                    </AccordionContent>
                  </AccordionItem>
                );
              })}
            </Accordion>
          )}
        </ScrollArea>
      </div>

      {/* Table Data Viewer Dialog */}
      <Dialog open={selectedTable !== null} onOpenChange={(open) => !open && setSelectedTable(null)}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Table2 className="h-5 w-5 text-primary" />
              Table: <span className="font-mono">{selectedTable}</span>
            </DialogTitle>
            <DialogDescription>
              Viewing all data from the {selectedTable} table
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-hidden">
            {renderTableDataView()}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

export default SchemaVisualizer;
