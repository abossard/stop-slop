export interface HealthModel { id: string; name: string; entities?: Entity[] }
export interface Entity { id: string; name: string; state: "healthy" | "degraded" | "unhealthy" | "unknown" }
export interface Relationship { id: string; parentId: string; childId: string }
