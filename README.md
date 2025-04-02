# 🗂️ File Organizer

A smart cross-platform desktop application (macOS + Windows) that intelligently analyzes and organizes your computer files using context and AI — with privacy and safety built in from the ground up.

---

## 🚀 Project Overview

**File Organizer** helps users tame digital clutter by scanning their folders, understanding the purpose of files using metadata and content, and suggesting the most intuitive and efficient folder structure. It only reorganizes files when the user explicitly approves the changes.

This project is in its early MVP phase. The long-term goal is to support:

- AI-assisted file categorization
- Secure dry-run previews
- Optional paid execution for full reorganization

---

## 🧠 How It Works (Planned Flow)

1. **User Onboarding** – User selects what kind of computer user they are and what types of files dominate their system (documents, media, code, etc.)
2. **File Scanning** – The app scans selected folders, gathering file metadata (name, type, date, size).
3. **Content Analysis** – For files like PDFs, TXT, DOCX, etc., the app optionally reads content for deeper context.
4. **AI-Powered Schema Generation** – Using local LLM processing or cloud APIs, the app proposes an optimal folder structure.
5. **Preview** – The user can interactively review and approve the proposed structure.
6. **Execution (Paid)** – Once approved, users can pay to unlock the actual file reorganization engine.
7. **Backup + Undo** – Original structure is saved so users can roll back changes if needed.

---

## 🛠 Tech Stack

| Layer                | Tech Used                                                |
| -------------------- | -------------------------------------------------------- |
| **Frontend**         | React (TypeScript), Vite                                 |
| **Backend (Native)** | Rust (via Tauri)                                         |
| **Desktop Shell**    | Tauri                                                    |
| **AI/LLM**           | OpenAI API (optional), or local inference via embeddings |
| **Build & Dev**      | Yarn, Git, GitHub                                        |

---

## ✅ Current Progress

- ✅ Tauri + React app scaffolded with `vite` and `TypeScript`
- ✅ First working Rust command using `tauri::command`
- ✅ Rust ↔ React bridge established (`invoke`)
- ✅ Project structure initialized (with `/src`, `/src-tauri`, etc.)
- ✅ Ready to add folder selection and scanning functionality

---

## 📁 Folder Structure

file-organizer/ ├── public/ ├── src/ │ ├── components/ │ ├── hooks/ │ ├── utils/ │ ├── pages/ │ └── App.tsx ├── src-tauri/ │ └── src/ │ └── main.rs ├── .github/ │ └── workflows/ ├── README.md ├── LICENSE ├── package.json ├── vite.config.ts └── tauri.conf.json

---

## 📌 Upcoming Features

- [ ] Folder selection dialog (native system picker)
- [ ] Recursive file scanning via Rust
- [ ] In-memory dry-run organization preview
- [ ] AI/LLM integration for schema generation
- [ ] Undo-safe move execution with file backups
- [ ] Stripe payment integration to unlock file reorganization

---

## 🤝 Contributing

This is a solo project (for now) — feedback, forks, and feature ideas are welcome.

---

## 🛡️ Privacy & Safety First

This application is being built with privacy as a first-class priority. All file analysis is done **locally by default**, and no content is uploaded without user consent. The goal is to build **trustworthy, secure, and non-destructive** file management tools.

---

<!-- ## 📄 License

MIT License © 2025 Jonathan Essis -->
