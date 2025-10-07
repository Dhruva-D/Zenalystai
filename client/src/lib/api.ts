/**
 * API configuration utility
 * Provides a centralized way to get the API base URL
 */

export const getApiUrl = (): string => {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  // Remove trailing slash if present
  return apiUrl.replace(/\/$/, '');
};

export const createApiEndpoint = (endpoint: string): string => {
  const baseUrl = getApiUrl();
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  return `${baseUrl}${cleanEndpoint}`;
};