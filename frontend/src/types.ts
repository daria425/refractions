export type APIFetchState = {
  loading: boolean;
  error: string | null;
  data: any;
};

export type GenerationSuccessResponse = {
  failed: number;
  total: number;
  results: any[];
  status: string;
  successful: number;
};
