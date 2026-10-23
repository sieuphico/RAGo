<script setup lang="ts">
// S-04 Kho tài liệu (library.html): 5 trạng thái — đang tải, trống, dữ liệu, lỗi, hạn chế quyền (US-015).
import { computed, onMounted, ref } from "vue";
import type { DocumentOut, DocumentSort } from "@/api/types";
import DocumentTable from "@/components/DocumentTable.vue";
import DropZone from "@/components/DropZone.vue";
import DuplicateDialog from "@/components/DuplicateDialog.vue";
import RowMenu from "@/components/RowMenu.vue";
import SummaryDialog from "@/components/SummaryDialog.vue";
import SkeletonRows from "@/components/SkeletonRows.vue";
import UploadQueue from "@/components/UploadQueue.vue";
import { useDocumentEvents } from "@/composables/useDocumentEvents";
import { useUpload } from "@/composables/useUpload";
import { t } from "@/content/messages";
import { useAuthStore } from "@/stores/auth";
import { useDocumentsStore } from "@/stores/documents";
import { useFeaturesStore } from "@/stores/features";

const auth = useAuthStore();
const docs = useDocumentsStore();
const features = useFeaturesStore();

const search = ref("");
const sort = ref<DocumentSort>("uploadedAt_desc");

const canUpload = computed(() => auth.me?.role === "TEAM_LEAD");
const upload = useUpload();
const { announcement } = useDocumentEvents();

// Tệp trùng tên và kích thước với tài liệu đã có (EC-10): hỏi từng tệp một.
const duplicates = ref<{ file: File; existing: DocumentOut }[]>([]);
const currentDuplicate = computed(() => duplicates.value[0] ?? null);

function findDuplicate(file: File): DocumentOut | undefined {
  return docs.items.find((d) => d.status !== "DELETED" && d.name === file.name && d.sizeBytes === file.size);
}

/** Tệp đã qua kiểm tra (T-508) → kiểm tra trùng (T-510, khi cờ bật) → hàng đợi tải lên (T-523). */
function onAccepted(files: File[]) {
  if (!features.flags.duplicateCheck) {
    upload.enqueue(files);
    return;
  }
  const fresh: File[] = [];
  for (const file of files) {
    const existing = findDuplicate(file);
    if (existing) duplicates.value.push({ file, existing });
    else fresh.push(file);
  }
  if (fresh.length > 0) upload.enqueue(fresh);
}

function resolveDuplicate(proceed: boolean) {
  const current = duplicates.value.shift();
  if (current && proceed) upload.enqueue([current.file]);
}

// Tóm tắt (T-518): chỉ tài liệu sẵn sàng và khi cờ `summary` bật.
const summaryDoc = ref<DocumentOut | null>(null);
const summaryOpen = ref(false);
const canSummarize = (d: DocumentOut): boolean =>
  features.flags.summary && d.status === "READY";
function openSummary(d: DocumentOut) {
  summaryDoc.value = d;
  summaryOpen.value = true;
}

const rows = computed(() => docs.filtered(search.value, sort.value));

onMounted(() => {
  void docs.fetch();
});
</script>

<template>
  <main id="main" class="page" data-testid="library">
    <div class="page-head">
      <h1>
        {{ t("library.title") }}
        <span class="muted count" data-testid="doc-count">({{ docs.items.length }})</span>
      </h1>
      <div class="field search-field">
        <label for="doc-search" class="sr-only">{{ t("library.searchLabel") }}</label>
        <input
          id="doc-search"
          v-model="search"
          class="input"
          type="search"
          autocomplete="off"
          :placeholder="t('library.searchPlaceholder')"
          data-testid="search"
        />
      </div>
    </div>

    <section v-if="canUpload" :aria-label="t('library.uploadAria')" data-testid="upload-slot">
      <DropZone @accepted="onAccepted" />
      <UploadQueue />
    </section>
    <p v-else class="note-line" data-testid="upload-not-allowed">{{ t("library.uploadNotAllowed") }}</p>

    <SkeletonRows v-if="docs.loading" :rows="5" />
    <div v-else-if="docs.error" class="state-box is-error" role="alert" data-testid="load-error">
      <strong>{{ t("library.loadError") }}</strong>
      <button type="button" class="btn" data-testid="retry" @click="docs.fetch()">{{ t("action.retry") }}</button>
    </div>
    <div v-else-if="docs.items.length === 0" class="state-box" data-testid="empty">
      <span aria-hidden="true" class="empty-icon">📄</span>
      <strong>{{ canUpload ? t("library.empty") : t("library.emptyNoUpload") }}</strong>
    </div>
    <template v-else>
      <DocumentTable :rows="rows" :sort="sort" :slow-ids="docs.slowIds" @sort="sort = $event">
        <template #actions="{ doc }">
          <RowMenu :doc="doc" :has-extra="canSummarize(doc)">
            <button
              v-if="canSummarize(doc)"
              type="button"
              role="menuitem"
              class="btn btn-ghost btn-sm"
              data-testid="menu-summary"
              @click="openSummary(doc)"
            >
              {{ t("rowmenu.summary") }}
            </button>
          </RowMenu>
        </template>
      </DocumentTable>
      <p v-if="rows.length === 0" class="muted no-match" data-testid="no-match">{{ t("library.noMatch") }}</p>
    </template>
    <div class="sr-only" aria-live="polite" data-testid="sr-live">{{ announcement }}</div>

    <SummaryDialog v-if="summaryDoc" :doc="summaryDoc" :open="summaryOpen" @close="summaryOpen = false" />

    <DuplicateDialog
      v-if="currentDuplicate"
      :key="currentDuplicate.file.name + currentDuplicate.file.size + duplicates.length"
      :file="currentDuplicate.file"
      :existing="currentDuplicate.existing"
      @cancel="resolveDuplicate(false)"
      @proceed="resolveDuplicate(true)"
    />
  </main>
</template>

<style scoped>
.count {
  font-weight: 400;
}
.search-field {
  min-width: 280px;
}
.empty-icon {
  font-size: 32px;
}
.no-match {
  padding: var(--space-4);
}
</style>
