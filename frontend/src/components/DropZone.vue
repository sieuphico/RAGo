<script setup lang="ts">
// Vùng kéo thả và nút chọn tệp cho Trưởng nhóm BD (CMP-14). Kiểm tra từng tệp trước khi gửi (EC-08).
import { ref } from "vue";
import { messageFor } from "@/api/errors";
import { track } from "@/api/telemetry";
import { t } from "@/content/messages";
import { telemetryReason, validateFiles, type Rejected } from "@/utils/validateFiles";

const emit = defineEmits<{ accepted: [files: File[]] }>();

const fileInput = ref<HTMLInputElement | null>(null);
const over = ref(false);
const rejected = ref<Rejected[]>([]);

function handle(list: FileList | File[] | null | undefined) {
  const files = list ? Array.from(list) : [];
  if (files.length === 0) return;
  const result = validateFiles(files);
  rejected.value = result.rejected;
  for (const r of result.rejected) track("document_upload_rejected", { reason: telemetryReason(r.code) });
  if (result.accepted.length > 0) emit("accepted", result.accepted);
}

function onChange(e: Event) {
  const input = e.target as HTMLInputElement;
  handle(input.files);
  input.value = ""; // cho phép chọn lại cùng tệp
}

function onDrop(e: DragEvent) {
  over.value = false;
  handle(e.dataTransfer?.files);
}
</script>

<template>
  <div
    class="dropzone"
    :class="{ 'is-over': over }"
    data-testid="dropzone"
    @dragover.prevent="over = true"
    @dragleave.prevent="over = false"
    @drop.prevent="onDrop"
  >
    <p>
      <strong>{{ t("upload.drop") }}</strong> {{ t("upload.or") }}
    </p>
    <button type="button" class="btn btn-primary" data-testid="pick" @click="fileInput?.click()">
      {{ t("upload.pick") }}
    </button>
    <input
      ref="fileInput"
      type="file"
      multiple
      accept="application/pdf,.pdf"
      class="sr-only"
      tabindex="-1"
      aria-hidden="true"
      data-testid="file-input"
      @change="onChange"
    />
    <p class="caption muted">{{ t("upload.limits") }}</p>
    <ul v-if="rejected.length" class="rejections caption" role="alert" data-testid="rejections">
      <li v-for="(r, i) in rejected" :key="i">{{ r.file.name }} – {{ messageFor(r.code) }}</li>
    </ul>
  </div>
</template>

<style scoped>
.rejections {
  list-style: none;
  margin: 0;
  padding: 0;
  color: var(--color-danger-text);
}
</style>
