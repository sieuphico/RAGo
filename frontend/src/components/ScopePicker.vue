<script setup lang="ts">
// Chọn phạm vi tài liệu (CMP-11, US-026): danh sách chọn nhiều, dùng được hoàn toàn bằng bàn phím. P1 (cờ `scope`).
import { computed, nextTick, ref, useId } from "vue";
import { t } from "@/content/messages";
import { useDocumentsStore } from "@/stores/documents";
import { normalizeText, truncateMiddle } from "@/utils/format";

const props = defineProps<{ modelValue: string[] }>();
const emit = defineEmits<{ "update:modelValue": [ids: string[]] }>();

const docs = useDocumentsStore();
const uid = useId();
const open = ref(false);
const filter = ref("");
const active = ref(0); // 0 = "Tất cả tài liệu"
const button = ref<HTMLButtonElement | null>(null);
const list = ref<HTMLElement | null>(null);

const label = computed(() =>
  props.modelValue.length === 0 ? t("scope.all") : t("scope.some", { N: props.modelValue.length }),
);
const options = computed(() => {
  const q = normalizeText(filter.value.trim());
  return docs.readyItems.filter((d) => !q || normalizeText(d.name).includes(q));
});
const optionId = (i: number) => `scope-${uid}-${i}`;

function isSelected(docId: string): boolean {
  return props.modelValue.includes(docId);
}

function toggleAt(i: number) {
  if (i === 0) {
    emit("update:modelValue", []);
    return;
  }
  const doc = options.value[i - 1];
  if (!doc) return;
  emit(
    "update:modelValue",
    isSelected(doc.docId) ? props.modelValue.filter((id) => id !== doc.docId) : [...props.modelValue, doc.docId],
  );
}

async function openList() {
  open.value = true;
  active.value = 0;
  await nextTick();
  list.value?.focus();
}

function closeList() {
  if (!open.value) return;
  open.value = false;
  filter.value = "";
  void nextTick(() => button.value?.focus());
}

function onButtonKey(e: KeyboardEvent) {
  if (e.key === "ArrowDown" && open.value) return;
  if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
    e.preventDefault();
    if (open.value) closeList();
    else void openList();
  }
}

function onKey(e: KeyboardEvent) {
  if (!open.value) return;
  const typing = e.target instanceof HTMLInputElement;
  const last = options.value.length; // chỉ số cuối (0 là "Tất cả")
  if (e.key === "Escape") {
    e.preventDefault();
    e.stopPropagation();
    closeList();
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    active.value = Math.min(last, active.value + 1);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    active.value = Math.max(0, active.value - 1);
  } else if ((e.key === " " || e.key === "Enter") && !typing) {
    e.preventDefault();
    toggleAt(active.value);
  }
}

function onFilter() {
  active.value = 0;
}

function onFocusOut(e: FocusEvent) {
  const root = (e.currentTarget as HTMLElement) ?? null;
  if (root && e.relatedTarget instanceof Node && !root.contains(e.relatedTarget)) open.value = false;
}
</script>

<template>
  <div class="scope-wrap" data-testid="scope-picker" @keydown="onKey" @focusout="onFocusOut">
    <button
      ref="button"
      type="button"
      class="btn btn-sm"
      aria-haspopup="listbox"
      :aria-expanded="open"
      data-testid="scope-button"
      @click="open ? closeList() : openList()"
      @keydown="onButtonKey"
    >
      {{ label }} <span aria-hidden="true">▾</span>
    </button>
    <div v-if="open" class="scope-list" data-testid="scope-popup">
      <input
        v-model="filter"
        class="input scope-filter"
        type="search"
        :aria-label="t('scope.filter')"
        :placeholder="t('scope.filter')"
        data-testid="scope-filter"
        @input="onFilter"
      />
      <ul
        ref="list"
        role="listbox"
        aria-multiselectable="true"
        tabindex="-1"
        :aria-label="t('scope.pickerAria')"
        :aria-activedescendant="optionId(active)"
        class="options"
        data-testid="scope-listbox"
      >
        <li
          :id="optionId(0)"
          role="option"
          :aria-selected="modelValue.length === 0"
          class="option"
          :class="{ active: active === 0 }"
          data-testid="scope-option-all"
          @click="toggleAt(0)"
        >
          {{ t("scope.allItem") }}
        </li>
        <li
          v-for="(d, i) in options"
          :id="optionId(i + 1)"
          :key="d.docId"
          role="option"
          :aria-selected="isSelected(d.docId)"
          class="option"
          :class="{ active: active === i + 1 }"
          data-testid="scope-option"
          :title="d.name"
          @click="toggleAt(i + 1)"
        >
          <span aria-hidden="true">{{ isSelected(d.docId) ? "☑" : "☐" }}</span> {{ truncateMiddle(d.name, 40) }}
        </li>
        <li v-if="options.length === 0" class="option muted" role="presentation">{{ t("scope.empty") }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.scope-filter {
  margin-bottom: var(--space-2);
}
.options {
  list-style: none;
  margin: 0;
  padding: 0;
}
.options:focus {
  outline: none;
}
.option {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  padding: var(--space-2);
  min-height: 32px;
  font-size: var(--font-caption);
  border-radius: var(--radius-control);
  cursor: pointer;
}
.option:hover,
.option.active {
  background: var(--color-surface);
}
.option[aria-selected="true"] {
  font-weight: 600;
}
.options:focus-visible .option.active {
  box-shadow: var(--focus-ring);
}
</style>
