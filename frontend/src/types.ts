export type GenerationSuccessResponse = {
  failed: number;
  total: number;
  results: ImageResult[];
  status: string;
  successful: number;
};

export type APIFetchState = {
  loading: boolean;
  error: string | null;
  data: GenerationSuccessResponse | null;
};
export type ImageResult = {
  shot_type?: string;
  label?: string;
  status: string;
  data: {
    image_url: string;
    seed: number;
    saved_path: string;
    structured_prompt: any;
    request_id: string;
  };
  error?: any;
};

export type VariantResult = {
  label: string;
  status: string;
  data: {
    image_url: string;
    seed: number;
    saved_path: string;
    structured_prompt: any;
    request_id: string;
  };
  error: any;
};

export type GeneratedImagesResults = {
  results: ImageResult[];
};

export type PromptEntry = {
  label: string;
  value: string;
  path: string;
};

export type EditorState = {
  activeEditor: string | null;
  editorContent?: any;
};

export type VariantItem = {
  variant_label: string;
  description: string;
};
export type ImageVariants = {
  [key: string]: VariantItem[];
};

export type VariantSchema = {
  version?: string;
  groups: ImageVariants;
};

// # CHANGE: Store complete edited image data for JSON comparison
export type EditedImageData = {
  saved_path: string;
  image_url?: string;
  structured_prompt: any;
  seed?: number;
  request_id?: string;
};
