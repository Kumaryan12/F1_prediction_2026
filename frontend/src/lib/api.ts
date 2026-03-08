import { promises as fs } from "fs";
import path from "path";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchSummary() {
  const res = await fetch(`${API_BASE}/summary`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch summary");
  return res.json();
}

export async function fetchTop10() {
  const res = await fetch(`${API_BASE}/predictions/top10`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch top 10");
  return res.json();
}

// Add this right next to your other fetch functions
export async function fetchLatestPredictions() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const res = await fetch(`${API_BASE}/predictions/latest`, { cache: "no-store" });
  
  if (!res.ok) {
    throw new Error("Failed to fetch full grid predictions");
  }
  
  return res.json();
}

export async function fetchFeatureImportance() {
  const filePath = path.join(process.cwd(), 'data', 'feature_importance_tree.csv'); 
  
  try {
    const fileContent = await fs.readFile(filePath, 'utf-8');
    const lines = fileContent.trim().split('\n');
    
    const features = lines.slice(1).map((line: string) => {
      if (!line.trim()) return null;

      const parts = line.split(','); 
      
      // We grab index 0 and 1 instead of 1 and 2
      const name = parts[0];
      const importance = parseFloat(parts[1]);
      
      return {
        name: name,
        value: importance
      };
    }).filter(Boolean); // Filter out the nulls

    return features;
  } catch (error) {
    console.error("Error reading CSV:", error);
    return []; 
  }
}

