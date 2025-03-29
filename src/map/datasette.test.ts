import { beforeEach, describe, it, vi, expect, afterEach } from "vitest";
import nock from "nock";
import { renderHook, waitFor } from "@testing-library/react";
import { DatasetteSqlResponse, useData } from "./datasette";

describe("useData", () => {
  beforeEach(() => {
    nock.disableNetConnect();
    vi.stubEnv("VITE_DATASETTE", "https://datasette.example.com/lotspy");
  });

  afterEach(() => {
    nock.isDone();
    nock.cleanAll();
    nock.enableNetConnect();
  });

  it("can load data", async () => {
    const scope = nock("https://datasette.example.com")
      .get("/lotspy.json")
      .query({
        sql: "select * from parcels limit :lim",
        lim: 2,
      })
      .delay(10)
      .reply(200, {
        database: "lotspy",
        query_name: null,
        rows: [
          [1, "parcel 1"],
          [2, "parcel 2"],
        ],
        columns: ["id", "name"],
        query: { sql: "", params: {} },
        private: false,
        allow_execute_sql: false,
        query_ms: 0,
        truncated: false,
        ok: true,
        error: null,
      } satisfies DatasetteSqlResponse);

    const params = { lim: 2 };
    const { result } = renderHook(() =>
      useData("select * from parcels limit :lim", params)
    );

    // start in a loading state
    expect(result.current).toEqual({
      isLoading: true,
      data: null,
      error: null,
    });

    // wait for the request to finish
    await waitFor(() =>
      expect(result.current).toEqual({
        isLoading: false,
        data: [
          {
            id: 1,
            name: "parcel 1",
          },
          {
            id: 2,
            name: "parcel 2",
          },
        ],
        error: null,
      })
    );

    scope.done();
  });

  it("handles api errors", async () => {
    const scope = nock("https://datasette.example.com")
      .get("/lotspy.json")
      .query({
        sql: "select * from parcels",
      })
      .reply(500, {
        database: "lotspy",
        query_name: null,
        rows: [
          [1, "parcel 1"],
          [2, "parcel 2"],
        ],
        columns: ["id", "name"],
        query: { sql: "", params: {} },
        private: false,
        allow_execute_sql: false,
        query_ms: 0,
        truncated: false,
        ok: false,
        error: "Internal Server Error",
      } satisfies DatasetteSqlResponse);

    const { result } = renderHook(() => useData("select * from parcels"));

    // start in a loading state
    expect(result.current).toEqual({
      isLoading: true,
      data: null,
      error: null,
    });

    // wait for the request to finish
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current).toMatchInlineSnapshot(`
      {
        "data": null,
        "error": [Error: Error 500: Internal Server Error],
        "isLoading": false,
      }
    `);
    scope.done();
  });

  it("handles network errors", async () => {
    // A network error will be triggered due to there being no nock

    const { result } = renderHook(() => useData("select * from parcels"));

    // start in a loading state
    expect(result.current).toEqual({
      isLoading: true,
      data: null,
      error: null,
    });

    // wait for the request to finish
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current).toMatchInlineSnapshot(`
      {
        "data": null,
        "error": [NetConnectNotAllowedError: Nock: Disallowed net connect for "datasette.example.com:443/lotspy.json?sql=select+*+from+parcels"],
        "isLoading": false,
      }
    `);
  });
});
