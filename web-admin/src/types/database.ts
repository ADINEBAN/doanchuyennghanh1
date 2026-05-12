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

export type Database = {
  public: {
    Tables: {
      profiles: { Row: Profile };
      companies: { Row: Company };
      vehicles: { Row: Vehicle };
      monitoring_sessions: { Row: MonitoringSession };
      alerts: { Row: Alert };
    };
  };
};
