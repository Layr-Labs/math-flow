/** Cloudflare Worker entry point for the vinext-starter template. */
import { handleImageOptimization, DEFAULT_DEVICE_SIZES, DEFAULT_IMAGE_SIZES } from "vinext/server/image-optimization";
import handler from "vinext/server/app-router-entry";

interface Env {
  ASSETS: Fetcher;
  MATH_FLOW_CATALOG_URL?: string;
  IMAGES: {
    input(stream: ReadableStream): {
      transform(options: Record<string, unknown>): {
        output(options: { format: string; quality: number }): Promise<{ response(): Response }>;
      };
    };
  };
}

interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
  passThroughOnException(): void;
}

// Image security config. SVG sources with .svg extension auto-skip the
// optimization endpoint on the client side (served directly, no proxy).
// To route SVGs through the optimizer (with security headers), set
// dangerouslyAllowSVG: true in next.config.js and uncomment below:
// const imageConfig: ImageConfig = { dangerouslyAllowSVG: true };

const worker = {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/api/catalog") {
      const source = env.MATH_FLOW_CATALOG_URL ??
        "https://raw.githubusercontent.com/mooselumph/math-flow/projections/viewer/catalog.json";
      try {
        const upstream = await fetch(source, {
          headers: { accept: "application/json", "cache-control": "no-cache" },
        });
        if (!upstream.ok) {
          return Response.json(
            { error: "repository catalog is unavailable", status: upstream.status },
            { status: 502, headers: { "cache-control": "no-store" } },
          );
        }
        return new Response(upstream.body, {
          headers: {
            "content-type": "application/json; charset=utf-8",
            "cache-control": "public, max-age=15, stale-while-revalidate=45",
            "x-math-flow-source": source,
          },
        });
      } catch {
        return Response.json(
          { error: "repository catalog could not be fetched" },
          { status: 502, headers: { "cache-control": "no-store" } },
        );
      }
    }

    if (url.pathname === "/_vinext/image") {
      const allowedWidths = [...DEFAULT_DEVICE_SIZES, ...DEFAULT_IMAGE_SIZES];
      return handleImageOptimization(request, {
        fetchAsset: (path) => env.ASSETS.fetch(new Request(new URL(path, request.url))),
        transformImage: async (body, { width, format, quality }) => {
          const result = await env.IMAGES.input(body).transform(width > 0 ? { width } : {}).output({ format, quality });
          return result.response();
        },
      }, allowedWidths);
    }

    return handler.fetch(request, env, ctx);
  },
};

export default worker;
