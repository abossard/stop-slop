export const api = {
  get: async <T>(path: string, query?: Record<string, string | undefined>): Promise<T> => { throw new Error(path + JSON.stringify(query)); },
  list: async <T>(path: string): Promise<T[]> => { throw new Error(path); },
};
export function notifyError(message: string, err: unknown): void { console.error(message, err); }
