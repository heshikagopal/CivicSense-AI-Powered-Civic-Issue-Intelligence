export type UserRole = 'citizen' | 'officer' | 'admin';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  department_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type IssueStatus = 'REPORTED' | 'VERIFIED' | 'IN_PROGRESS' | 'RESOLVED' | 'REJECTED';
export type PriorityBand = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface IssueCategory {
  id: string;
  code: string;
  display_name: string;
  description?: string;
  base_risk_score: number;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  contact_email?: string;
}

export interface Ward {
  id: string;
  ward_number: number;
  name: string;
  population_density_level: string;
}

export interface Issue {
  id: string;
  issue_code: string;
  category_id: string;
  category_code?: string;
  category_name?: string;
  ward_id?: string;
  ward_name?: string;
  title: string;
  description?: string;
  status: IssueStatus;
  latitude: float;
  longitude: float;
  address?: string;
  priority_score: number;
  priority_band: PriorityBand;
  report_count: number;
  assigned_department_id?: string;
  assigned_department_name?: string;
  assigned_officer_id?: string;
  first_reported_at: string;
  last_reported_at: string;
  resolved_at?: string;
  verified_at?: string;
  created_at: string;
}

type float = number;

export interface DetectionBox {
  category_code: string;
  category_name: string;
  confidence: number;
  bbox: [number, number, number, number];
  status: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface DetectionResult {
  detections: DetectionBox[];
  model_version: string;
  inference_ms: number;
  preview_url?: string;
  suggested_category?: string;
  confidence_tier: 'HIGH' | 'MEDIUM' | 'LOW';
  is_civic_defect_detected?: boolean;
  detection_notes?: string;
}

export interface DuplicateCandidate {
  match_id?: string;
  candidate_issue_id: string;
  issue_code: string;
  category_name: string;
  status: string;
  latitude: number;
  longitude: number;
  address?: string;
  distance_meters: number;
  time_difference_hours: number;
  visual_similarity: number;
  overall_duplicate_score: number;
  recommended_action: 'AUTO_LINK' | 'MANUAL_REVIEW' | 'NEW_ISSUE';
  primary_image_url?: string;
}

export interface PriorityFactorScore {
  score: number;
  weight_percent: number;
  weighted_contribution: number;
  description: string;
}

export interface PriorityBreakdown {
  issue_id: string;
  overall_score: number;
  priority_band: PriorityBand;
  is_overridden: boolean;
  override_reason?: string;
  factors: Record<string, PriorityFactorScore>;
}

export interface Report {
  id: string;
  report_code: string;
  issue_id?: string;
  user_id?: string;
  user_latitude: number;
  user_longitude: number;
  address_text?: string;
  image_url: string;
  citizen_category_suggestion?: string;
  citizen_comment?: string;
  status: string;
  created_at: string;
}

export interface IssueDetail extends Issue {
  reports: Report[];
  recent_detections: any[];
  assignments: any[];
  resolutions: any[];
}

export interface AnalyticsSummary {
  total_issues: number;
  pending_issues: number;
  verified_issues: number;
  in_progress_issues: number;
  resolved_issues: number;
  duplicate_reports_identified: number;
  average_resolution_hours: number;
  high_critical_count: number;
}

export interface MapIssuePoint {
  id: string;
  issue_code: string;
  title: string;
  category_code: string;
  category_name: string;
  status: string;
  latitude: number;
  longitude: number;
  priority_score: number;
  priority_band: PriorityBand;
  report_count: number;
  image_url?: string;
  created_at: string;
}

export interface HotspotCluster {
  cluster_id: number;
  center_lat: number;
  center_lng: number;
  radius_meters: number;
  issue_count: number;
  dominant_category: string;
  average_priority: number;
  severity_level: 'LOW' | 'MODERATE' | 'HIGH' | 'SEVERE';
}
