import type { ServerResponse } from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const webRoot = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  resolve: {
    alias: {
      // Ensure browser voice session setup (mic/worklet/WebSocket) is registered in prod builds.
      "@elevenlabs/client": path.resolve(
        webRoot,
        "node_modules/@elevenlabs/client/dist/platform/web/index.js",
      ),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8780",
        changeOrigin: true,
        /** Vite/http-proxy default is HTTP 500 + empty body on ECONNREFUSED — unusable for debugging. */
        configure(proxy) {
          proxy.on("error", (err, _req, res) => {
            const r = res as ServerResponse | undefined;
            if (!r || r.headersSent) return;
            const msg =
              err instanceof Error ? err.message : String(err);
            r.writeHead(502, { "Content-Type": "application/json" });
            r.end(
              JSON.stringify({
                detail:
                  `Dev proxy could not reach the API at http://127.0.0.1:8780 (${msg}). ` +
                  "Start uvicorn from demo/realtime-sales-demo/server (see run-demo.ps1), then retry.",
              }),
            );
          });
        },
      },
      "/debug": {
        target: "http://127.0.0.1:8780",
        changeOrigin: true,
      },
      "/admin": {
        target: "http://127.0.0.1:8780",
        changeOrigin: true,
      },
    },
  },
});
