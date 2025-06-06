import axios from "axios";

const API_URL = "http://localhost:8765";

export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

class ApiService {
  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${API_URL}/`);
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async startScan(
    path: string,
    maxFiles: number = 1000
  ): Promise<TaskResponse> {
    const response = await axios.post(`${API_URL}/api/scan`, {
      path,
      max_files: maxFiles,
    });
    return response.data;
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await axios.get(`${API_URL}/api/task/${taskId}`);
    return response.data;
  }

  async getScanResults(taskId: string): Promise<any> {
    const response = await axios.get(`${API_URL}/api/scan/${taskId}/results`);
    return response.data;
  }

  async generatePrompt(path: string): Promise<TaskResponse> {
    const response = await axios.post(`${API_URL}/api/prompt`, {
      path,
      use_cached_scan: true,
    });
    return response.data;
  }

  async loadPlan(): Promise<any> {
    const response = await axios.get(`${API_URL}/api/plan/load`);
    return response.data;
  }

  async savePlan(plan: any): Promise<any> {
    const response = await axios.post(`${API_URL}/api/plan/save`, { plan });
    return response.data;
  }

  async executeOrganization(
    path: string,
    dryRun: boolean = true
  ): Promise<TaskResponse> {
    const response = await axios.post(`${API_URL}/api/organize`, {
      path,
      dry_run: dryRun,
    });
    return response.data;
  }

  async getConfig(): Promise<any> {
    const response = await axios.get(`${API_URL}/api/config`);
    return response.data;
  }

  async listBackups(): Promise<any> {
    const response = await axios.get(`${API_URL}/api/backups`);
    return response.data;
  }

  async createBackup(path: string, name?: string): Promise<any> {
    const response = await axios.post(`${API_URL}/api/backup`, {
      path,
      backup_name: name,
    });
    return response.data;
  }

  async restoreBackup(manifestFile?: string): Promise<any> {
    const response = await axios.post(`${API_URL}/api/revert`, {
      manifest_file: manifestFile,
    });
    return response.data;
  }

  subscribeToTask(
    taskId: string,
    onUpdate: (data: TaskStatus) => void
  ): EventSource {
    const eventSource = new EventSource(`${API_URL}/api/events/${taskId}`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
    };
    return eventSource;
  }
}

export const api = new ApiService();
export type { TaskResponse as TaskResponseType };
export type { TaskStatus as TaskStatusType };
