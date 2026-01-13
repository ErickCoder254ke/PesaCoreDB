import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/components/theme-provider";
import DatabaseInterface from "@/components/DatabaseInterface";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="rdbms-theme">
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<DatabaseInterface />} />
          </Routes>
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;
