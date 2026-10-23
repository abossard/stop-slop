import { api, notifyError } from "./api";
import type { Entity, HealthModel, Relationship } from "./types";

/** Loads a health model, either without entities or full. Notifies on API errors. */
export async function loadHealthModel(id: string, full = false): Promise<HealthModel | undefined> {
  try {
    return await api.get<HealthModel>(`/models/${id}`, { expand: full ? "entities" : undefined });
  } catch (err) {
    notifyError("Could not load health model", err);
    return undefined;
  }
}

/** Loads all entities of a model. Notifies on API errors. */
export async function loadEntities(modelId: string): Promise<Entity[]> {
  try {
    return await api.list<Entity>(`/models/${modelId}/entities`);
  } catch (err) {
    notifyError("Could not load entities", err);
    return [];
  }
}

/** Loads the relationships of a model. Notifies on API errors. */
export async function loadRelationships(modelId: string): Promise<Relationship[]> {
  try {
    return await api.list<Relationship>(`/models/${modelId}/relationships`);
  } catch (err) {
    notifyError("Could not load relationships", err);
    return [];
  }
}
