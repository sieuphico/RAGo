<script setup lang="ts">
// Hộp thoại xác nhận bằng <dialog> + showModal(): giam focus, Esc đóng, trả focus về phần tử đã mở.
import { nextTick, ref, useId, watch } from "vue";
import { t } from "@/content/messages";

const props = defineProps<{ open: boolean; title: string; confirmLabel: string; destructive?: boolean }>();
const emit = defineEmits<{ confirm: []; cancel: [] }>();

const dlg = ref<HTMLDialogElement | null>(null);
const cancelBtn = ref<HTMLButtonElement | null>(null);
const confirmBtn = ref<HTMLButtonElement | null>(null);
const titleId = `dlg-title-${useId()}`;
let opener: HTMLElement | null = null;

watch(
  () => props.open,
  async (isOpen) => {
    const el = dlg.value;
    if (!el) return;
    if (isOpen) {
      opener = document.activeElement instanceof HTMLElement ? document.activeElement : null;
      if (!el.open) el.showModal();
      await nextTick();
      // Thao tác phá hủy: focus mặc định ở "Hủy" (Blueprint 3.8.2).
      (props.destructive ? cancelBtn.value : confirmBtn.value)?.focus();
    } else {
      if (el.open) el.close();
      opener?.focus();
      opener = null;
    }
  },
  { immediate: true, flush: "post" },
);

function onCancel(e: Event) {
  e.preventDefault(); // phần cha quyết định đóng bằng prop `open`
  emit("cancel");
}
</script>

<template>
  <dialog
    ref="dlg"
    aria-modal="true"
    :aria-labelledby="titleId"
    data-testid="confirm-dialog"
    @cancel="onCancel"
    @keydown.esc.prevent="emit('cancel')"
  >
    <h2 :id="titleId">{{ title }}</h2>
    <div class="dlg-body"><slot /></div>
    <div class="dlg-actions">
      <button ref="cancelBtn" type="button" class="btn" data-testid="dialog-cancel" @click="emit('cancel')">
        {{ t("action.cancel") }}
      </button>
      <button
        ref="confirmBtn"
        type="button"
        class="btn"
        :class="destructive ? 'btn-danger' : 'btn-primary'"
        data-testid="dialog-confirm"
        @click="emit('confirm')"
      >
        {{ confirmLabel }}
      </button>
    </div>
  </dialog>
</template>
