# 🗂️ File Organizer (Electron + Python)

An intelligent, cross-platform desktop app that scans, understands, and reorganizes your computer files based on context and user preferences. Built with Electron (React) for the frontend and Python for the backend logic.

---

## 🎯 Project Goal

Make it dead simple for anyone to:

- Select a folder
- Automatically categorize and preview a smarter organization
- Approve or tweak the proposed structure
- Apply changes (safely, with backup)
- Optionally use AI to improve recommendations

---

## 🔧 Tech Stack

| Layer         | Technology                    |
| ------------- | ----------------------------- |
| Frontend      | Electron + React (TypeScript) |
| Backend       | Python 3 (via child process)  |
| Communication | `child_process.spawn()`       |
| File Access   | Node.js FS + Python OS libs   |
| Packaging     | `electron-builder`            |

---

## 🧠 Core Features

- 📁 Select any folder on your machine
- 🔍 Python script scans all files: name, type, size, modified date
- 🧠 Tags files based on logic or LLMs (optional)
- 📂 Proposes a new intuitive folder structure (dry run)
- 👁️ View the plan, approve or tweak it
- ✅ Execute reorganization safely (with full backup + undo)

---

## 🛣️ Roadmap

### ✅ Phase 1: MVP (Manual Logic)

- [x] Project setup (Electron + React + TypeScript)
- [x] Connect to Python script via child process
- [ ] Build folder selection UI
- [ ] Use Python to scan files in selected folder
- [ ] Return metadata (name, type, size, dates)
- [ ] Display results in frontend
- [ ] Group files into categories (in memory)
- [ ] Preview proposed structure
- [ ] Execute move (with undo + backup)
- [ ] Package the app

### 🔮 Phase 2: Smart Logic & AI

- [ ] Add AI-powered tagging (via GPT or local embeddings)
- [ ] Add user profiles ("I’m a dev", "I’m a student", etc.)
- [ ] Let user define rules for organization
- [ ] Offer “paid execution” model to finalize reorg

---

## 🧪 Dev Instructions

### 1. Install

```bash
npm install
```

### 2. Run Dev Server

```bash
npm run start
```

### 3. Run Python Script Test

```bash
python backend/scanner.py ~/Desktop/TestFolder
```

---

## 📁 File Structure

```
file-organizer/
├── backend/
│   └── scanner.py         # Python file scanner logic
├── public/
├── src/
│   ├── main/              # Electron main process
│   ├── renderer/          # React frontend
├── package.json
└── README.md
```

---

## 🛡️ Privacy First

All file scanning and logic is run locally. No files or metadata are sent to the cloud.

---

## 📄 License

MIT © 2025
