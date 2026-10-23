<script setup lang="ts">
// Huy hiệu trạng thái tài liệu (CMP-16, CONTRACTS 10.3): luôn có chữ và biểu tượng, không chỉ màu.
import { computed } from "vue";
import type { ClientUploadState, DocumentStatus, FailureReason } from "@/api/types";
import { messageFor } from "@/api/errors";
import { t } from "@/content/messages";
import IconGlyph from "./IconGlyph.vue";
import type { IconName } from "./icons";

const props = defineProps<{
  status: DocumentStatus | ClientUploadState;
  progress?: number;
  failureReason?: FailureReason | null;
  /** OCR quá 15 phút (EC-20): thêm "Xử lý lâu bất thường". */
  slow?: boolean;
}>();

interface View {
  tone: "info" | "warning" | "success" | "danger" | "neutral";
  icon: IconName;
  label: string;
  note?: string;
}

const view = computed<View>(() => {
  switch (props.status) {
    case "UPLOADING":
      return { tone: "info", icon: "up", label: t("status.uploading", { p: Math.round(props.progress ?? 0) }) };
    case "INTERRUPTED":
      return { tone: "warning", icon: "warn", label: t("status.interrupted") };
    case "PROCESSING":
      return { tone: "info", icon: "spin", label: t("status.processing") };
    case "OCR_PROCESSING":
      return {
        tone: "info",
        icon: "ocr",
        label: props.slow ? `${t("status.ocr")} · ${t("status.ocrSlow")}` : t("status.ocr"),
        note: t("status.ocrNote"),
      };
    case "READY":
      return { tone: "success", icon: "check", label: t("status.ready") };
    case "FAILED": {
      const reason = props.failureReason ?? "PROCESSING_ERROR";
      return {
        tone: "danger",
        icon: "x",
        label: t("status.failed", { "lý do": messageFor(reason) }),
        note: reason === "OCR_UNREADABLE" ? t("status.ocrHint") : undefined,
      };
    }
    default:
      return { tone: "neutral", icon: "x", label: t("status.deleted") };
  }
});
</script>

<template>
  <span class="status-wrap">
    <span class="badge" :class="`badge-${view.tone}`" :title="view.note" :data-status="status" data-testid="status-badge">
      <IconGlyph :name="view.icon" />
      <span class="badge-label">{{ view.label }}</span>
    </span>
    <span v-if="view.note" class="caption muted badge-note">{{ view.note }}</span>
  </span>
</template>

<style scoped>
.status-wrap {
  display: inline-flex;
  flex-direction: column;
  gap: var(--space-1);
  align-items: flex-start;
}
</style>
