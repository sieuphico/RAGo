import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from "@vue/eslint-config-typescript";

export default defineConfigWithVueTs(
  { ignores: ["dist/**", "coverage/**", "node_modules/**", "playwright-report/**", "test-results/**", "e2e/**"] },
  js.configs.recommended,
  pluginVue.configs["flat/recommended"],
  vueTsConfigs.recommended,
  {
    files: ["**/*.vue"],
    rules: {
      // Quy ước CONTRACTS 10.6: nội dung AI và tên tệp không bao giờ dùng v-html.
      "vue/no-v-html": "error",
      "vue/multi-word-component-names": "off",
      "vue/max-attributes-per-line": "off",
      "vue/singleline-html-element-content-newline": "off",
      "vue/html-self-closing": "off",
      "vue/html-indent": "off",
      "vue/html-closing-bracket-newline": "off",
      "vue/first-attribute-linebreak": "off",
    },
  },
  {
    rules: {
      // Không ghi nội dung vào console (AGENTS.md).
      "no-console": ["error", { allow: ["warn"] }],
    },
  },
  {
    // Script công cụ chạy bằng Node.
    files: ["scripts/**/*.mjs"],
    languageOptions: { globals: { console: "readonly", process: "readonly", URL: "readonly" } },
    rules: { "no-console": "off" },
  },
);
