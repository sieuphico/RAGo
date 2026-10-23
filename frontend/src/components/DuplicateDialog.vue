<script setup lang="ts">
// Cảnh báo tệp trùng tên và kích thước (EC-10, BR-001). P1 (cờ `duplicateCheck`).
import type { DocumentOut } from "@/api/types";
import { t } from "@/content/messages";
import { formatDate, formatMegabytes } from "@/utils/format";
import ConfirmDialog from "./ConfirmDialog.vue";

defineProps<{ file: File; existing: DocumentOut }>();
const emit = defineEmits<{ cancel: []; proceed: [] }>();
</script>

<template>
  <ConfirmDialog
    :open="true"
    :title="t('duplicate.title')"
    :confirm-label="t('duplicate.proceed')"
    @confirm="emit('proceed')"
    @cancel="emit('cancel')"
  >
    <span data-testid="duplicate-body">{{
      t("duplicate.body", { tên: file.name, cỡ: formatMegabytes(file.size), ngày: formatDate(existing.uploadedAt) })
    }}</span>
  </ConfirmDialog>
</template>
