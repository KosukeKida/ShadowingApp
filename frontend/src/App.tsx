import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MaterialList } from "./components/MaterialList";
import { YouTubeImport } from "./components/YouTubeImport";
import { PdfImport } from "./components/PdfImport";
import { PracticeView } from "./components/PracticeView";
import { BookOpen, Headphones } from "lucide-react";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppContent() {
  const [selectedMaterialId, setSelectedMaterialId] = useState<number | null>(
    null
  );

  if (selectedMaterialId !== null) {
    return (
      <PracticeView
        materialId={selectedMaterialId}
        onBack={() => setSelectedMaterialId(null)}
      />
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="flex items-center justify-center gap-3 mb-2">
          <Headphones className="h-8 w-8 text-primary" />
          <h1 className="text-3xl font-bold">Shadowing Practice</h1>
        </div>
        <p className="text-muted-foreground">
          Improve your English pronunciation with AI-powered feedback
        </p>
      </div>

      {/* Import Section */}
      <div className="grid gap-4 md:grid-cols-2">
        <YouTubeImport />
        <PdfImport />
      </div>

      {/* Material Library */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="h-5 w-5" />
          <h2 className="text-xl font-semibold">Material Library</h2>
        </div>
        <MaterialList onSelectMaterial={setSelectedMaterialId} />
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-8 px-4 max-w-5xl">
          <AppContent />
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
