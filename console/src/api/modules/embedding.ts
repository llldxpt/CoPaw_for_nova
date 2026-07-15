import { request } from "../request";

export interface EmbeddingConfigRequest {
  provider_id: string;
  model_name: string;
  dimensions: number;
  enable_cache: boolean;
  use_dimensions: boolean;
  max_input_length: number;
  max_batch_size: number;
  base_url: string;
  api_key?: string;
}

export interface EmbeddingConfigResponse {
  provider_id: string | null;
  model_name: string | null;
  dimensions: number;
  enable_cache: boolean;
  use_dimensions: boolean;
  max_input_length: number;
  max_batch_size: number;
  base_url: string;
  api_key: string;
}

export interface SetActiveRequest {
  provider_id: string;
  base_url: string;
  model_name: string;
  dimensions: number;
  enable_cache: boolean;
  use_dimensions: boolean;
  max_input_length: number;
  max_batch_size: number;
  api_key?: string;
}

export interface TestEmbeddingRequest {
  provider_id: string;
  base_url: string;
  model_name: string;
}

export interface TestEmbeddingResponse {
  success: boolean;
  message: string;
}

export const embeddingApi = {
  getEmbeddingConfig: () =>
    request<EmbeddingConfigResponse | null>("/embeddings/config", {
      method: "GET",
    }),

  saveEmbeddingConfig: (body: EmbeddingConfigRequest) =>
    request<EmbeddingConfigResponse>("/embeddings/config", {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  setActiveEmbedding: (body: SetActiveRequest) =>
    request<EmbeddingConfigResponse>("/embeddings/active", {
      method: "PUT",
      body: JSON.stringify(body),
    }),

  testEmbeddingConnection: (body: TestEmbeddingRequest) =>
    request<TestEmbeddingResponse>("/embeddings/test", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
