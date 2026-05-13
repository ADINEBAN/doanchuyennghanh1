export type UserRole = "SUPER_ADMIN" | "COMPANY_ADMIN" | "DRIVER";

export type UserStatus = "active" | "inactive" | "locked";

export type VehicleStatus = "available" | "assigned" | "maintenance" | "inactive";

export type SessionStatus = "running" | "stopped" | "interrupted";

export type RiskLevel = "low" | "medium" | "high" | "danger";

export type AlertType =
  | "closed_eyes"
  | "yawning"
  | "drowsy"
  | "distracted"
  | "face_not_detected";

export type Profile = {
  id: string;
  email: string;
  username: string | null;
  full_name: string | null;
  phone: string | null;
  avatar_url: string | null;
  role: UserRole;
  status: UserStatus;
  company_id: string | null;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Company = {
  id: string;
  name: string;
  address: string | null;
  phone: string | null;
  email: string | null;
  logo_url: string | null;
  description: string | null;
  status: "active" | "inactive" | "locked";
  created_at: string;
  updated_at: string;
};

export type CompanyInsert = {
  name: string;
  address?: string | null;
  phone?: string | null;
  email?: string | null;
  logo_url?: string | null;
  description?: string | null;
  status?: "active" | "inactive" | "locked";
};

export type CompanyUpdate = Partial<CompanyInsert>;

export type Vehicle = {
  id: string;
  company_id: string;
  license_plate: string;
  brand: string | null;
  model: string | null;
  color: string | null;
  year: number | null;
  status: VehicleStatus;
  assigned_driver_id: string | null;
  created_at: string;
  updated_at: string;
};

export type VehicleInsert = {
  company_id: string;
  license_plate: string;
  brand?: string | null;
  model?: string | null;
  color?: string | null;
  year?: number | null;
  status?: VehicleStatus;
  assigned_driver_id?: string | null;
};

export type VehicleUpdate = Partial<VehicleInsert>;

export type MonitoringSession = {
  id: string;
  user_id: string;
  company_id: string | null;
  vehicle_id: string | null;
  started_at: string;
  ended_at: string | null;
  status: SessionStatus;
  duration_seconds: number | null;
  total_alerts: number | null;
  closed_eyes_count: number | null;
  yawning_count: number | null;
  drowsy_count: number | null;
  distraction_count: number | null;
  face_not_detected_count: number | null;
};

export type Alert = {
  id: string;
  user_id: string;
  session_id: string;
  company_id: string | null;
  vehicle_id: string | null;
  alert_type: AlertType;
  risk_level: RiskLevel;
  status_label: string;
  triggered_at: string;
  ear_value: number | null;
  mar_value: number | null;
  ai_label: string | null;
  ai_confidence: number | null;
  head_yaw: number | null;
  head_pitch: number | null;
};

export type DriverLiveStatus = {
  driver_id: string;
  session_id: string | null;
  company_id: string | null;
  vehicle_id: string | null;
  is_app_online: boolean;
  is_monitoring: boolean;
  status: string;
  risk_level: RiskLevel;
  ear_value: number | null;
  mar_value: number | null;
  head_yaw: number | null;
  head_pitch: number | null;
  last_seen_at: string;
  updated_at: string;
};

export type AIModel = {
  id: string;
  name: string;
  version: string | null;
  file_path: string;
  file_format: "h5" | "keras" | "pt" | "onnx" | "tflite";
  description: string | null;
  accuracy: number | null;
  precision_score: number | null;
  recall_score: number | null;
  f1_score: number | null;
  num_classes: number | null;
  class_labels: string | null;
  is_default: boolean | null;
  status: "active" | "inactive" | "testing";
  created_by: string | null;
  created_at: string;
  updated_at: string;
};

export type AIModelInsert = {
  name: string;
  version?: string | null;
  file_path: string;
  file_format?: AIModel["file_format"];
  description?: string | null;
  accuracy?: number | null;
  precision_score?: number | null;
  recall_score?: number | null;
  f1_score?: number | null;
  num_classes?: number | null;
  class_labels?: string | null;
  is_default?: boolean | null;
  status?: AIModel["status"];
  created_by?: string | null;
};

export type SystemSetting = {
  id: string;
  key: string;
  value: string;
  data_type: "string" | "int" | "float" | "boolean" | "json";
  description: string | null;
  updated_by: string | null;
  updated_at: string;
};

export type UserSettings = {
  id: string;
  user_id: string;
  ear_threshold: number;
  ear_consec_frames: number;
  mar_threshold: number;
  yawn_consec_frames: number;
  ai_prediction_interval: number;
  drowsy_alert_seconds: number;
  head_yaw_threshold: number;
  head_pitch_threshold: number;
  distraction_seconds: number;
  face_not_detected_seconds: number;
  selected_model_name: string | null;
  alert_sound_enabled: boolean;
  alert_sound_path: string | null;
  camera_index: number;
  created_at: string;
  updated_at: string;
};

export type UserSettingsInsert = {
  user_id: string;
  ear_threshold?: number;
  ear_consec_frames?: number;
  mar_threshold?: number;
  yawn_consec_frames?: number;
  ai_prediction_interval?: number;
  drowsy_alert_seconds?: number;
  head_yaw_threshold?: number;
  head_pitch_threshold?: number;
  distraction_seconds?: number;
  face_not_detected_seconds?: number;
  selected_model_name?: string | null;
  alert_sound_enabled?: boolean;
  alert_sound_path?: string | null;
  camera_index?: number;
};

export type Database = {
  public: {
    Tables: {
      profiles: { Row: Profile; Insert: Partial<Profile>; Update: Partial<Profile> };
      companies: { Row: Company; Insert: CompanyInsert; Update: CompanyUpdate };
      vehicles: { Row: Vehicle; Insert: VehicleInsert; Update: VehicleUpdate };
      monitoring_sessions: {
        Row: MonitoringSession;
        Insert: Partial<MonitoringSession>;
        Update: Partial<MonitoringSession>;
      };
      alerts: { Row: Alert; Insert: Partial<Alert>; Update: Partial<Alert> };
      ai_models: { Row: AIModel; Insert: AIModelInsert; Update: Partial<AIModelInsert> };
      system_settings: {
        Row: SystemSetting;
        Insert: Partial<SystemSetting>;
        Update: Partial<SystemSetting>;
      };
      user_settings: {
        Row: UserSettings;
        Insert: UserSettingsInsert;
        Update: Partial<UserSettingsInsert>;
      };
      driver_live_status: {
        Row: DriverLiveStatus;
        Insert: Partial<DriverLiveStatus>;
        Update: Partial<DriverLiveStatus>;
      };
    };
  };
};
