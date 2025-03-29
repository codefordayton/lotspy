import { useEffect, useState } from "react";

export function getDatasetteUrl() {
  const url = import.meta.env.VITE_DATASETTE;
  return url ?? "http://localhost:8001/lotspy";
}

/**
 * Response from Datasette API
 */
export type DatasetteSqlResponse = {
  database: string;
  query_name: string | null;
  rows: Array<Array<string | number>>;
  truncated: boolean;
  columns: Array<string>;
  query: {
    sql: string;
    params: Record<string, string | number>;
  };
  private: boolean;
  allow_execute_sql: boolean;
  query_ms: number;
} & (
  | {
      ok: true;
      error: null;
    }
  | {
      ok: false;
      error: string;
    }
);

export type Row = Record<string, string | number>;

/**
 * Possible responses from the useData hook
 */
export type UseDataResponse<T extends Row> =
  | {
      isLoading: true;
      data: null;
      error: null;
    }
  | {
      isLoading: false;
      data: T[];
      error: null;
    }
  | {
      isLoading: false;
      data: null;
      error: Error;
    };

/**
 * Fetches data from datasette
 */
export function useData<T extends Row>(
  query: string,
  params?: Record<string, string | number>
): UseDataResponse<T> {
  const [response, setResponse] = useState<UseDataResponse<T>>({
    isLoading: true,
    data: null,
    error: null,
  });

  useEffect(() => {
    async function fetchData() {
      const url = new URL(`${getDatasetteUrl()}.json`);
      url.searchParams.set("sql", query);

      for (const key in params) {
        url.searchParams.set(key, String(params[key]));
      }

      setResponse({
        isLoading: true,
        data: null,
        error: null,
      });

      try {
        const res = await fetch(url);
        if (!res.ok) {
          throw new Error(`Error ${res.status}: ${res.statusText}`);
        }

        const data = (await res.json()) as DatasetteSqlResponse;
        if (!data.ok) {
          throw new Error(data.error);
        }

        // Convert rows to objects
        const rows = data.rows.map((rowRaw) => {
          const rowObject: Row = {};
          data.columns.forEach((column, index) => {
            rowObject[column] = rowRaw[index];
          });
          return rowObject as T;
        });

        setResponse({
          isLoading: false,
          data: rows,
          error: null,
        });
      } catch (error) {
        console.error("Error fetching data from Datasette", error);

        let cleanedError: Error;
        if (error instanceof Error) {
          cleanedError = error
        } else {
          cleanedError = new Error("Unknown error");
        }

        setResponse({
          isLoading: false,
          data: null,
          error: cleanedError,
        });
      }
    }

    fetchData();
  }, [query, params]);

  return response;
}
