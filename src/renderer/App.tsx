import React, { useState } from 'react';
const { ipcRenderer } = window.require('electron');

function App() {
  const [files, setFiles] = useState<any[]>([]);
  const [folder, setFolder] = useState<string>('');

  const selectFolder = async () => {
    const folderPath = await ipcRenderer.invoke('select-folder');
    if (!folderPath) return;

    setFolder(folderPath);
    const scannedFiles = await ipcRenderer.invoke('scan-folder', folderPath);
    setFiles(scannedFiles);
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>🗂 File Organizer</h1>
      <button onClick={selectFolder}>Select Folder</button>
      {folder && <p><strong>Selected:</strong> {folder}</p>}
      <ul>
        {files.map((file, index) => (
          <li key={index}>
            {file.name} – {Math.round((file.size || 0) / 1024)} KB
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
