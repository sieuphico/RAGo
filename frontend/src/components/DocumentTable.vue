<script setup lang="ts">
import type { DocumentOut, DocumentSort } from "@/api/types";
import { t } from "@/content/messages";
import { formatDateTime, truncateMiddle } from "@/utils/format";
import StatusBadge from "./StatusBadge.vue";

const props = defineProps<{ rows: DocumentOut[]; sort: DocumentSort; slowIds?: Set<string> }>();
const emit = defineEmits<{ sort: [s: DocumentSort] }>();

function ariaSort(col: "name" | "uploadedAt"): "ascending" | "descending" | "none" {
  if (props.sort === `${col}_asc`) return "ascending";
  if (props.sort === `${col}_desc`) return "descending";
  return "none";
}

function toggle(col: "name" | "uploadedAt") {
  emit("sort", props.sort === `${col}_asc` ? `${col}_desc` : `${col}_asc`);
}

function arrow(col: "name" | "uploadedAt"): string {
  const s = ariaSort(col);
  return s === "ascending" ? "↑" : s === "descending" ? "↓" : "↕";
}
</script>

<template>
  <div class="table-wrap">
    <table class="table" data-testid="doc-table">
      <caption class="sr-only">{{ t("library.caption") }}</caption>
      <thead>
        <tr>
          <th scope="col" :aria-sort="ariaSort('name')">
            <button type="button" class="btn btn-ghost btn-sm" data-testid="sort-name" @click="toggle('name')">
              {{ t("library.col.name") }} <span aria-hidden="true">{{ arrow("name") }}</span>
            </button>
          </th>
          <th scope="col" class="num">{{ t("library.col.pages") }}</th>
          <th scope="col">{{ t("library.col.uploader") }}</th>
          <th scope="col" :aria-sort="ariaSort('uploadedAt')">
            <button type="button" class="btn btn-ghost btn-sm" data-testid="sort-time" @click="toggle('uploadedAt')">
              {{ t("library.col.time") }} <span aria-hidden="true">{{ arrow("uploadedAt") }}</span>
            </button>
          </th>
          <th scope="col">{{ t("library.col.status") }}</th>
          <th scope="col"><span class="sr-only">{{ t("library.col.actions") }}</span></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in rows" :key="doc.docId" data-testid="doc-row">
          <td><span class="doc-name" :title="doc.name" data-testid="doc-name">{{ truncateMiddle(doc.name, 40) }}</span></td>
          <td class="num" data-testid="doc-pages">{{ doc.pageCount ?? "—" }}</td>
          <td data-testid="doc-uploader">{{ doc.uploadedBy }}</td>
          <td data-testid="doc-time">{{ formatDateTime(doc.uploadedAt) }}</td>
          <td>
            <StatusBadge
              :status="doc.status"
              :failure-reason="doc.failureReason"
              :slow="slowIds?.has(doc.docId)"
            />
          </td>
          <td class="row-actions"><slot name="actions" :doc="doc" /></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
