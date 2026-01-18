import { useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { materialsApi } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Loader2, Upload } from "lucide-react";

export function PdfImport() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const importMutation = useMutation({
    mutationFn: (file: File) => materialsApi.importPdf(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["materials"] });
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === "application/pdf") {
      importMutation.mutate(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-500" />
          Import PDF
        </CardTitle>
      </CardHeader>
      <CardContent>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
        />
        <Button
          onClick={handleClick}
          disabled={importMutation.isPending}
          variant="outline"
          className="w-full"
        >
          {importMutation.isPending ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Processing PDF...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4 mr-2" />
              Select PDF File
            </>
          )}
        </Button>
        {importMutation.isError && (
          <p className="text-sm text-destructive mt-2">
            Failed to import PDF. Please try again.
          </p>
        )}
        {importMutation.isSuccess && (
          <p className="text-sm text-green-600 mt-2">
            Successfully imported!
          </p>
        )}
      </CardContent>
    </Card>
  );
}
