import axios, { AxiosInstance } from "axios";

const API_BASE_URL = "http://localhost:8765/api";

export interface ScanRequest {
  path: string;
  maxFiles?: number;
}

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

export interface ScanResult {
  total_files: number;
  organized_folders: number;
  file_types: Record<string, number>;
}

export interface OrganizationPlan {
  folders: string[];
  moves: Array<{
    file: string;
    relative_path: string;
    new_path: string;
    reason: string;
  }>;
}

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  // Health check
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get("/");
      return response.status === 200;
    } catch {
      return false;
    }
  }

  // Scanning
  async startScan(request: ScanRequest): Promise<TaskResponse> {
    const response = await this.client.post<TaskResponse>("/scan", request);
    return response.data;
  }

  async getScanResults(taskId: string): Promise<any> {
    const response = await this.client.get(`/scan/${taskId}/results`);
    return response.data;
  }

  // Task management
  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response = await this.client.get<TaskStatus>(`/task/${taskId}`);
    return response.data;
  }

  async listTasks(): Promise<any> {
    const response = await this.client.get("/tasks");
    return response.data;
  }

  // Prompt generation
  async generatePrompt(path: string): Promise<TaskResponse> {
    const response = await this.client.post<TaskResponse>("/prompt", {
      path,
      use_cached_scan: true,
    });
    return response.data;
  }

  // Organization
  async validatePlan(path: string, plan: OrganizationPlan): Promise<any> {
    const response = await this.client.post("/plan/validate", { path, plan });
    return response.data;
  }

  async savePlan(path: string, plan: OrganizationPlan): Promise<any> {
    const response = await this.client.post("/plan/save", { path, plan });
    return response.data;
  }

  async executeOrganization(
    path: string,
    dryRun: boolean = true
  ): Promise<TaskResponse> {
    const response = await this.client.post<TaskResponse>("/organize", {
      path,
      dry_run: dryRun,
    });
    return response.data;
  }

  // Backups
  async createBackup(path: string, name?: string): Promise<any> {
    const response = await this.client.post("/backup", {
      path,
      backup_name: name,
    });
    return response.data;
  }

  async listBackups(): Promise<any> {
    const response = await this.client.get("/backups");
    return response.data;
  }

  // Configuration
  async getConfig(): Promise<any> {
    const response = await this.client.get("/config");
    return response.data;
  }

  // Server-sent events for real-time updates
  subscribeToTask(
    taskId: string,
    onUpdate: (data: TaskStatus) => void
  ): EventSource {
    const eventSource = new EventSource(`${API_BASE_URL}/events/${taskId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
    };

    return eventSource;
  }
}

export const api = new ApiService();
