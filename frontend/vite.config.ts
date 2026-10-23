/// <reference types="vitest/config" />
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Máy chủ phát triển chuyển tiếp /api và /auth sang backend (cổng 8000).
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
  },
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: false },
      "/auth": { target: "http://localhost:8000", changeOrigin: false },
    },
  },
  test: {
    environment: "jsdom",
    globals: false,
    include: ["src/**/*.spec.ts"],
    restoreMocks: true,
    setupFiles: ["src/__tests__/setup.ts"],
  },
});
