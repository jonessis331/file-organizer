// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// fn main() {
//     file_organizer_lib::run()
// }

use std::fs;
use std::path::PathBuf;
use tauri::command;
use serde::Serialize;

#[derive(Serialize)]
struct FileMeta {
    name: String,
    path: String,
    file_type: String,
    size: u64,
    created: String,
    modified: String,
}

#[command]
fn scan_directory(path: String) -> Vec<FileMeta> {
    let mut files = Vec::new();
    visit_dirs(PathBuf::from(path), &mut files);
    files
}

fn visit_dirs(dir: PathBuf, files: &mut Vec<FileMeta>) {
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                visit_dirs(path, files);
            } else if let Ok(metadata) = entry.metadata() {
                let created = metadata.created().ok()
                    .and_then(|c| Some(format!("{:?}", c)))
                    .unwrap_or("unknown".into());
                let modified = metadata.modified().ok()
                    .and_then(|m| Some(format!("{:?}", m)))
                    .unwrap_or("unknown".into());
                files.push(FileMeta {
                    name: entry.file_name().to_string_lossy().to_string(),
                    path: path.to_string_lossy().to_string(),
                    file_type: path.extension()
                        .and_then(|ext| ext.to_str())
                        .unwrap_or("unknown").to_string(),
                    size: metadata.len(),
                    created,
                    modified,
                });
            }
        }
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![scan_directory])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
        
      
}
