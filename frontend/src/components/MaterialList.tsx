import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { materialsApi } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Trash2, Play, Youtube, FileText, File } from "lucide-react";

interface MaterialListProps {
  onSelectMaterial: (id: number) => void;
}

export function MaterialList({ onSelectMaterial }: MaterialListProps) {
  const queryClient = useQueryClient();

  const { data: materials, isLoading } = useQuery({
    queryKey: ["materials"],
    queryFn: () => materialsApi.list().then((res) => res.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => materialsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["materials"] });
    },
  });

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case "youtube":
        return <Youtube className="h-5 w-5 text-red-500" />;
      case "pdf":
        return <FileText className="h-5 w-5 text-blue-500" />;
      default:
        return <File className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!materials || materials.length === 0) {
    return (
      <div className="text-center p-8 text-muted-foreground">
        <p>No materials yet.</p>
        <p className="text-sm mt-2">
          Import a YouTube video or PDF to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {materials.map((material) => (
        <Card key={material.id} className="overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                {getSourceIcon(material.source_type)}
                <CardTitle className="text-lg line-clamp-2">
                  {material.title}
                </CardTitle>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {formatDuration(material.duration)}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onSelectMaterial(material.id)}
                >
                  <Play className="h-4 w-4 mr-1" />
                  Practice
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => deleteMutation.mutate(material.id)}
                  disabled={deleteMutation.isPending}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
