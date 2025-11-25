export type APIFetchState = {
  loading: boolean;
  error: string | null;
  data: any;
};

export type GenerationSuccessResponse = {
  failed: number;
  total: number;
  results: ImageResult[];
  status: string;
  successful: number;
};

export type ImageResult = {
  shot_type: string;
  status: string;
  data: {
    image_url: string;
    seed: number;
    structured_prompt: any;
    request_id: string;
  };
  error?: any;
};

export type GeneratedImagesResults = {
  results: ImageResult[];
};

export type PromptEntry = {
  label: string;
  value: string;
  path: string;
};
