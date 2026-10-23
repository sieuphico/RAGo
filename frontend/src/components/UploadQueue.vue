<script setup lang="ts">
// Các tệp đang tải lên ở đầu bảng kho (CONTRACTS 10.3): "Đang tải lên (p%)" hoặc "Tải lên bị gián đoạn" + [Thử lại].
import { computed } from "vue";
import { messageFor } from "@/api/errors";
import { t } from "@/content/messages";
import { useUpload } from "@/composables/useUpload";
import { truncateMiddle } from "@/utils/format";
import StatusBadge from "./StatusBadge.vue";

const upload = useUpload();
const visible = computed(() => upload.items.value.filter((i) => i.state !== "DONE"));
</script>

<template>
  <ul v-if="visible.length" class="upload-queue" :aria-label="t('upload.queueAria')" data-testid="upload-queue">
    <li v-for="item in visible" :key="item.id" class="upload-row" data-testid="upload-row">
      <span class="doc-name" :title="item.file.name">{{ truncateMiddle(item.file.name, 40) }}</span>
      <template v-if="item.state === 'UPLOADING'">
        <StatusBadge status="UPLOADING" :progress="item.progress" />
        <progress class="upload-progress" max="100" :value="item.progress" :aria-label="item.file.name"></progress>
      </template>
      <template v-else-if="item.state === 'INTERRUPTED'">
        <StatusBadge status="INTERRUPTED" />
        <button type="button" class="btn btn-sm" data-testid="upload-retry" @click="upload.retry(item.id)">
          {{ t("action.retry") }}
        </button>
      </template>
      <template v-else>
        <span class="badge badge-danger" role="alert" data-testid="upload-rejected">{{ messageFor(item.errorCode ?? "INTERNAL") }}</span>
        <button type="button" class="btn btn-ghost btn-sm" @click="upload.dismiss(item.id)">{{ t("upload.dismiss") }}</button>
      </template>
    </li>
  </ul>
</template>

<style scoped>
.upload-queue {
  list-style: none;
  margin: 0 0 var(--space-4);
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.upload-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  padding: var(--space-2) var(--space-3);
  background: var(--color-surface);
  border-radius: var(--radius-control);
  font-size: var(--font-caption);
}
.upload-row .doc-name {
  flex: 1;
  min-width: 160px;
  font-weight: 600;
}
.upload-progress {
  width: 120px;
}
</style>
