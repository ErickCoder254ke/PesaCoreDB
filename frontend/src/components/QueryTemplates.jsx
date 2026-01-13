import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "@/components/ui/sonner";
import {
  FileCode,
  Copy,
  Check,
  Code2,
  Sparkles,
} from "lucide-react";
import { SQL_QUERY_TEMPLATES } from "@/lib/sql-knowledge-base";
import { cn } from "@/lib/utils";

const QueryTemplates = ({ onSelectQuery, className }) => {
  const [copiedId, setCopiedId] = useState(null);

  const handleCopyTemplate = (template, idx) => {
    navigator.clipboard.writeText(template.example);
    setCopiedId(idx);
    toast.success("Template copied to clipboard!");
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleInsertTemplate = (template) => {
    if (onSelectQuery) {
      onSelectQuery(template.example);
      toast.success("Template inserted into editor!");
    }
  };

  return (
    <Card className={cn("border-primary/20 shadow-lg h-full flex flex-col", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <FileCode className="h-5 w-5 text-primary" />
          Query Templates
        </CardTitle>
        <CardDescription className="text-xs">
          Pre-built SQL templates for common operations
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
            <TabsContent 
              key={category} 
              value={category} 
              className="flex-1 overflow-hidden mt-2 px-4 pb-4"
            >
              <ScrollArea className="h-full">
                <div className="space-y-2 pr-4">
                  {SQL_QUERY_TEMPLATES
                    .filter((template) => category === "all" || template.category === category)
                    .map((template, idx) => (
                      <Card
                        key={idx}
                        className="cursor-pointer transition-all hover:border-primary/50 hover:shadow-md group"
                      >
                        <CardContent className="p-3">
                          <div className="flex items-start justify-between gap-2 mb-2">
                            <h4 className="font-semibold text-sm">{template.title}</h4>
                            <Badge variant="outline" className="text-xs flex-shrink-0">
                              {template.category}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mb-2">
                            {template.description}
                          </p>
                          <div className="bg-muted p-2 rounded-md mb-2 overflow-x-auto">
                            <code className="text-xs font-mono block whitespace-pre-wrap break-all">
                              {template.example}
                            </code>
                          </div>
                          <div className="flex gap-2">
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="flex-1 h-7 text-xs gap-1.5"
                                    onClick={() => handleInsertTemplate(template)}
                                  >
                                    <Code2 className="w-3 h-3" />
                                    Insert
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Insert into SQL editor</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>

                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="h-7 text-xs gap-1.5"
                                    onClick={() => handleCopyTemplate(template, idx)}
                                  >
                                    {copiedId === idx ? (
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
                                </TooltipTrigger>
                                <TooltipContent>
                                  <p>Copy to clipboard</p>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
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
  );
};

export default QueryTemplates;
