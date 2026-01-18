import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { materialsApi } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Youtube, Loader2 } from "lucide-react";

export function YouTubeImport() {
  const [url, setUrl] = useState("");
  const queryClient = useQueryClient();

  const importMutation = useMutation({
    mutationFn: (url: string) => materialsApi.importYoutube(url),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["materials"] });
      setUrl("");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      importMutation.mutate(url.trim());
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Youtube className="h-5 w-5 text-red-500" />
          Import from YouTube
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={importMutation.isPending}
            className="flex-1"
          />
          <Button type="submit" disabled={importMutation.isPending || !url.trim()}>
            {importMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Importing...
              </>
            ) : (
              "Import"
            )}
          </Button>
        </form>
        {importMutation.isError && (
          <p className="text-sm text-destructive mt-2">
            Failed to import. Please check the URL and try again.
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
