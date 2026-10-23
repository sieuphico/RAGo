<script setup lang="ts">
// Nội dung câu trả lời (CMP-07). Nội dung do AI tạo là dữ liệu không tin cậy: luôn dựng bằng nút văn bản, không dùng HTML thô.
import { computed } from "vue";
import type { CitationOut, UiMessage } from "@/api/types";
import { splitAnswer } from "@/utils/answerText";
import CitationChip from "./CitationChip.vue";

const props = defineProps<{ message: UiMessage }>();
const emit = defineEmits<{ open: [c: CitationOut] }>();

const parts = computed(() => splitAnswer(props.message.text));

function citationFor(index: number): CitationOut | undefined {
  return props.message.citations.find((c) => c.index === index);
}
</script>

<template>
  <div class="msg-ai" data-testid="answer-block">
    <div v-if="message.text" class="answer-body">
      <p class="answer-text" :class="{ caret: message.state === 'STREAMING' }" data-testid="answer-text">
<template
          v-for="(part, i) in parts"
          :key="i"
        >
<template v-if="part.kind === 'text'">{{ part.value }}</template><template v-else-if="citationFor(part.index)">
<CitationChip
            :citation="citationFor(part.index)!"
            @open="emit('open', $event)"
          />
</template>
</template>
</p>
    </div>
    <slot name="state" />
    <slot name="actions" />
  </div>
</template>

<style scoped>
.answer-text {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
</style>
