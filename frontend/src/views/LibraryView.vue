<script setup lang="ts">
// S-04 Kho tài liệu (library.html): 5 trạng thái — đang tải, trống, dữ liệu, lỗi, hạn chế quyền (US-015).
import { computed, onMounted, ref } from "vue";
import type { DocumentSort } from "@/api/types";
import DocumentTable from "@/components/DocumentTable.vue";
import DropZone from "@/components/DropZone.vue";
import SkeletonRows from "@/components/SkeletonRows.vue";
import UploadQueue from "@/components/UploadQueue.vue";
import { useDocumentEvents } from "@/composables/useDocumentEvents";
import { useUpload } from "@/composables/useUpload";
import { t } from "@/content/messages";
import { useAuthStore } from "@/stores/auth";
import { useDocumentsStore } from "@/stores/documents";

const auth = useAuthStore();
const docs = useDocumentsStore();

const search = ref("");
const sort = ref<DocumentSort>("uploadedAt_desc");

const canUpload = computed(() => auth.me?.role === "TEAM_LEAD");
const upload = useUpload();
const { announcement } = useDocumentEvents();
/** Tệp đã qua kiểm tra (T-508) → hàng đợi tải lên (T-523). */
function onAccepted(files: File[]) {
  upload.enqueue(files);
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
        <!-- Menu thao tác theo dòng (T-510, T-518) gắn vào slot "actions" -->
      </DocumentTable>
      <p v-if="rows.length === 0" class="muted no-match" data-testid="no-match">{{ t("library.noMatch") }}</p>
    </template>
    <div class="sr-only" aria-live="polite" data-testid="sr-live">{{ announcement }}</div>
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
