<script setup lang="ts">
// Menu thao tác theo dòng của kho tài liệu (⋯): Xóa (chỉ khi `canDelete`), các mục khác qua slot (T-518 thêm "Tóm tắt").
import { nextTick, ref } from "vue";
import { ApiError, request } from "@/api/client";
import { messageFor } from "@/api/errors";
import type { DocumentOut } from "@/api/types";
import { useToast } from "@/composables/useToast";
import { t } from "@/content/messages";
import { useDocumentsStore } from "@/stores/documents";
import ConfirmDialog from "./ConfirmDialog.vue";
import IconGlyph from "./IconGlyph.vue";

const props = defineProps<{ doc: DocumentOut; hasExtra?: boolean }>();
const emit = defineEmits<{ deleted: [docId: string] }>();

const docs = useDocumentsStore();
const toast = useToast();
const menuOpen = ref(false);
const confirmOpen = ref(false);
const busy = ref(false);
const trigger = ref<HTMLButtonElement | null>(null);
const menu = ref<HTMLElement | null>(null);

function items(): HTMLElement[] {
  return menu.value ? Array.from(menu.value.querySelectorAll<HTMLElement>("[role=menuitem]")) : [];
}

async function toggle() {
  menuOpen.value = !menuOpen.value;
  if (menuOpen.value) {
    await nextTick();
    items()[0]?.focus();
  }
}

function closeMenu(restore = true) {
  if (!menuOpen.value) return;
  menuOpen.value = false;
  if (restore) void nextTick(() => trigger.value?.focus());
}

function onMenuKey(e: KeyboardEvent) {
  const list = items();
  const i = list.indexOf(document.activeElement as HTMLElement);
  if (e.key === "Escape") {
    e.preventDefault();
    e.stopPropagation();
    closeMenu();
  } else if (e.key === "ArrowDown") {
    e.preventDefault();
    list[(i + 1) % list.length]?.focus();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    list[(i - 1 + list.length) % list.length]?.focus();
  }
}

function onFocusOut(e: FocusEvent) {
  const root = e.currentTarget as HTMLElement;
  if (e.relatedTarget instanceof Node && !root.contains(e.relatedTarget)) closeMenu(false);
}

function askDelete() {
  closeMenu(false);
  confirmOpen.value = true;
}

async function confirmDelete() {
  if (busy.value) return;
  busy.value = true;
  confirmOpen.value = false;
  try {
    const res = await request<{ docId: string; alreadyDeleted: boolean }>(
      `/api/v1/documents/${encodeURIComponent(props.doc.docId)}`,
      { method: "DELETE" },
    );
    if (res.alreadyDeleted) toast.show(t("delete.already"));
    docs.remove(props.doc.docId);
    emit("deleted", props.doc.docId);
  } catch (e) {
    toast.show(messageFor(e instanceof ApiError ? e.code : "INTERNAL"), "error");
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="row-menu" data-testid="row-menu" @focusout="onFocusOut" @keydown="menuOpen && onMenuKey($event)">
    <!-- Dòng thất bại: nút Xóa hiện trực tiếp (wireframe) -->
    <button
      v-if="doc.status === 'FAILED' && doc.canDelete && !hasExtra"
      type="button"
      class="btn btn-ghost btn-sm danger-text"
      :aria-label="t('rowmenu.deleteAria', { tên: doc.name })"
      data-testid="delete-direct"
      @click="askDelete"
    >
      <IconGlyph name="trash" /> {{ t("rowmenu.delete") }}
    </button>
    <template v-else-if="doc.canDelete || hasExtra">
      <button
        ref="trigger"
        type="button"
        class="btn btn-ghost btn-icon"
        aria-haspopup="menu"
        :aria-expanded="menuOpen"
        :aria-label="t('rowmenu.aria', { tên: doc.name })"
        data-testid="menu-trigger"
        @click="toggle"
      >
        <span aria-hidden="true">⋯</span>
      </button>
      <div v-if="menuOpen" ref="menu" class="menu" role="menu" data-testid="menu">
        <slot />
        <button v-if="doc.canDelete" type="button" role="menuitem" class="btn btn-ghost btn-sm danger-text" data-testid="menu-delete" @click="askDelete">
          <IconGlyph name="trash" /> {{ t("rowmenu.delete") }}
        </button>
      </div>
    </template>

    <ConfirmDialog
      v-if="doc.canDelete"
      :open="confirmOpen"
      :title="t('delete.title')"
      :confirm-label="t('delete.confirm')"
      destructive
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    >
      {{ t("delete.body", { tên: doc.name }) }}
    </ConfirmDialog>
  </div>
</template>

<style scoped>
.row-menu {
  position: relative;
  display: inline-block;
}
.menu {
  position: absolute;
  right: 0;
  top: calc(100% + 4px);
  z-index: 15;
  min-width: 160px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--space-1);
  padding: var(--space-2);
  background: var(--color-white);
  border: 1px solid var(--color-border-control);
  border-radius: var(--radius-card);
  box-shadow: 0 4px 16px rgba(31, 41, 55, 0.12);
}
.menu .btn {
  justify-content: flex-start;
}
.danger-text {
  color: var(--color-danger-text);
}
</style>
