import { useEffect, useState } from 'react';
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";

type FileMeta = {
  name: string;
  path: string;
  file_type: string;
  size: number;
  created: string;
  modified: string;
};

export default function App() {
  const [files, setFiles] = useState<FileMeta[]>([]);
  const [folder, setFolder] = useState<string | null>(null);

  const selectFolder = async () => {
    console.log("🟡 Button clicked: opening folder dialog...");
  
    try {
      const selected = await open({ directory: true });
      console.log("🟢 Folder selected:", selected);
  
      if (typeof selected === "string") {
        setFolder(selected);
        const result = await invoke<FileMeta[]>("scan_directory", { path: selected });
        console.log("📁 Files returned:", result);
        setFiles(result);
      } else {
        console.log("🟠 No folder selected or dialog was cancelled");
      }
    } catch (error) {
      console.error("🔴 Error selecting folder:", error);
    }
  };
  

  return (
    <div style={{ padding: 24 }}>
      <h1>📁 File Organizer</h1>
      <button onClick={selectFolder}>Select Folder</button>
      {folder && <p>Selected: {folder}</p>}

      {files.length > 0 && (
        <>
          <h2>Scanned Files</h2>
          <ul>
            {files.map((file, i) => (
              <li key={i}>
                <strong>{file.name}</strong> — {file.file_type} — {Math.round(file.size / 1024)} KB
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
