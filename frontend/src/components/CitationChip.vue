<script setup lang="ts">
// Thẻ trích dẫn bấm được (CMP-08): `[Tên tài liệu – tr. N]`. Chỉ hiển thị văn bản, không bao giờ HTML.
import { computed } from "vue";
import type { CitationOut } from "@/api/types";
import { t } from "@/content/messages";
import { truncateMiddle } from "@/utils/format";

const props = defineProps<{ citation: CitationOut }>();
const emit = defineEmits<{ open: [c: CitationOut] }>();

const label = computed(() =>
  props.citation.deleted
    ? t("citation.deleted")
    : `[${truncateMiddle(props.citation.docName, 24)} – tr. ${props.citation.page}]`,
);
const aria = computed(() =>
  props.citation.deleted
    ? t("citation.deleted")
    : t("citation.aria", { "tên tài liệu": props.citation.docName, N: props.citation.page }),
);
const snippet = computed(() => props.citation.snippet.slice(0, 200));
</script>

<template>
  <button
    type="button"
    class="citation"
    :class="{ 'is-deleted': citation.deleted }"
    :disabled="citation.deleted"
    :aria-label="aria"
    :title="citation.docName"
    data-testid="citation"
    @click="emit('open', citation)"
  >
    <span class="cit-label" data-testid="citation-label">{{ label }}</span>
    <span v-if="!citation.deleted && snippet" class="tip" aria-hidden="true">{{ snippet }}</span>
  </button>
</template>
