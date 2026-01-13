import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/sonner";
import DatabaseInterface from "@/components/DatabaseInterface";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="pesacodedb-theme">
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<DatabaseInterface />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" richColors closeButton expand={false} />
      </div>
    </ThemeProvider>
  );
}

export default App;
