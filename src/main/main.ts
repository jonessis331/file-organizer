import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import * as path from 'path';
import { spawn } from 'child_process';

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  win.loadURL('http://localhost:3000'); // Replace if you're bundling locally
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle('select-folder', async () => {
    const result = await dialog.showOpenDialog({ properties: ['openDirectory'] });
    return result.filePaths[0];
  });

  ipcMain.handle('scan-folder', async (event, folderPath) => {
    return new Promise((resolve, reject) => {
      const python = spawn('python3', ['backend/scanner.py', folderPath]);

      let output = '';
      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (err) => {
        console.error('Python error:', err.toString());
      });

      python.on('close', () => {
        try {
          const parsed = JSON.parse(output);
          resolve(parsed);
        } catch (e) {
          reject('Failed to parse Python output.');
        }
      });
    });
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
