import { useState, useEffect } from "react";
import apiClient from "@/lib/api-client";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/sonner";
import {
  Database,
  Plus,
  Trash2,
  Loader2,
  Info,
} from "lucide-react";
import { cn } from "@/lib/utils";


export default function DatabaseSelector({ currentDatabase, onDatabaseChange }) {
  const [databases, setDatabases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [newDatabaseName, setNewDatabaseName] = useState("");
  const [databaseToDelete, setDatabaseToDelete] = useState(null);
  const [databaseInfo, setDatabaseInfo] = useState(null);

  useEffect(() => {
    fetchDatabases();
  }, []);

  useEffect(() => {
    if (currentDatabase) {
      fetchDatabaseInfo(currentDatabase);
    }
  }, [currentDatabase]);

  const fetchDatabases = async () => {
    try {
      const response = await apiClient.get('/databases');
      setDatabases(response.data.databases || []);
    } catch (err) {
      console.error("Failed to fetch databases:", err);
      toast.error("Failed to load databases");
    }
  };

  const fetchDatabaseInfo = async (dbName) => {
    try {
      const response = await apiClient.get(`/databases/${dbName}/info`);
      setDatabaseInfo(response.data);
    } catch (err) {
      console.error("Failed to fetch database info:", err);
      setDatabaseInfo(null);
    }
  };

  const handleCreateDatabase = async () => {
    if (!newDatabaseName.trim()) {
      toast.error("Database name cannot be empty");
      return;
    }

    setLoading(true);

    try {
      await apiClient.post('/databases', { name: newDatabaseName.trim() });
      toast.success(`Database '${newDatabaseName}' created successfully`);
      setNewDatabaseName("");
      setCreateDialogOpen(false);
      await fetchDatabases();
      onDatabaseChange(newDatabaseName.trim());
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create database");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDatabase = async () => {
    if (!databaseToDelete) return;

    setLoading(true);

    try {
      await apiClient.delete(`/databases/${databaseToDelete}`);
      toast.success(`Database '${databaseToDelete}' deleted successfully`);
      setDeleteDialogOpen(false);
      setDatabaseToDelete(null);
      await fetchDatabases();

      // Switch to default if deleted current database
      if (currentDatabase === databaseToDelete) {
        onDatabaseChange("default");
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to delete database");
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = (dbName) => {
    setDatabaseToDelete(dbName);
    setDeleteDialogOpen(true);
  };

  return (
    <div className="database-selector-container">
      {/* Database Selector */}
      <div className="database-selector-controls flex items-center gap-3">
        <div className="flex-1 min-w-[200px]">
          <Label htmlFor="database-select" className="text-xs text-muted-foreground mb-1 block">
            Active Database
          </Label>
          <Select value={currentDatabase} onValueChange={onDatabaseChange}>
            <SelectTrigger id="database-select" className="database-select-trigger">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-primary" />
                <SelectValue placeholder="Select database" />
              </div>
            </SelectTrigger>
            <SelectContent className="database-select-content">
              {databases.map((db) => (
                <SelectItem key={db} value={db} className="database-select-item">
                  <div className="flex items-center justify-between w-full gap-2">
                    <span>{db}</span>
                    {db === "default" && (
                      <Badge variant="secondary" className="text-xs">
                        Default
                      </Badge>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Database Info */}
        {databaseInfo && (
          <div className="database-info-badge flex items-center gap-2 text-xs text-muted-foreground">
            <Info className="h-3 w-3" />
            <span>
              {databaseInfo.table_count} table{databaseInfo.table_count !== 1 ? 's' : ''}, {databaseInfo.total_rows} row{databaseInfo.total_rows !== 1 ? 's' : ''}
            </span>
          </div>
        )}

        {/* Create Database Button */}
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm" className="create-db-button gap-2">
              <Plus className="h-4 w-4" />
              <span className="hidden sm:inline">New Database</span>
            </Button>
          </DialogTrigger>
          <DialogContent className="create-db-dialog">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                Create New Database
              </DialogTitle>
              <DialogDescription>
                Enter a name for your new database. Use only letters, numbers, underscores, and hyphens.
              </DialogDescription>
            </DialogHeader>
            <div className="database-name-input-container py-4">
              <Label htmlFor="database-name" className="mb-2 block">
                Database Name
              </Label>
              <Input
                id="database-name"
                value={newDatabaseName}
                onChange={(e) => setNewDatabaseName(e.target.value)}
                placeholder="my_database"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !loading) {
                    handleCreateDatabase();
                  }
                }}
                className="database-name-input"
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setCreateDialogOpen(false);
                  setNewDatabaseName("");
                }}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button onClick={handleCreateDatabase} disabled={loading} className="gap-2">
                {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                Create Database
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Database Button */}
        {currentDatabase && currentDatabase !== "default" && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => confirmDelete(currentDatabase)}
            className="delete-db-button text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="delete-db-confirm-dialog">
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <Trash2 className="h-5 w-5 text-destructive" />
              Delete Database
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the database <strong>'{databaseToDelete}'</strong>?
              This action cannot be undone and all tables and data will be permanently deleted.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={loading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteDatabase}
              disabled={loading}
              className={cn(
                "bg-destructive text-destructive-foreground hover:bg-destructive/90",
                loading && "opacity-50"
              )}
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              Delete Database
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
