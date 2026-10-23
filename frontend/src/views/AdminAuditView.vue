<script setup lang="ts">
// S-08 Nhật ký tải lên và xóa tài liệu: 4 trường (ai, thao tác, tài liệu, thời điểm), chỉ Quản trị viên (US-063, BR-018).
import { onMounted, ref } from "vue";
import { request } from "@/api/client";
import type { AuditOut } from "@/api/types";
import AdminTabs from "@/components/AdminTabs.vue";
import SkeletonRows from "@/components/SkeletonRows.vue";
import { M, t } from "@/content/messages";
import { formatDateTime } from "@/utils/format";

const items = ref<AuditOut[]>([]);
const loading = ref(true);
const failed = ref(false);

async function load() {
  loading.value = true;
  failed.value = false;
  try {
    const data = await request<{ items: AuditOut[] }>("/api/v1/admin/audit-log?limit=100");
    items.value = data.items;
  } catch {
    failed.value = true;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <main id="main" class="page" data-testid="admin-audit">
    <AdminTabs />
    <div class="page-head"><h1>{{ t("audit.title") }}</h1></div>

    <SkeletonRows v-if="loading" :rows="3" />
    <div v-else-if="failed" class="state-box is-error" role="alert" data-testid="load-error">
      <strong>{{ t("audit.loadError") }}</strong>
      <button type="button" class="btn" data-testid="retry" @click="load">{{ t("action.retry") }}</button>
    </div>
    <div v-else-if="items.length === 0" class="state-box" data-testid="empty">
      <strong>{{ t("audit.empty") }}</strong>
    </div>
    <div v-else class="table-wrap">
      <table class="table" data-testid="audit-table">
        <caption class="sr-only">{{ t("audit.caption") }}</caption>
        <thead>
          <tr>
            <th scope="col">{{ t("audit.colActor") }}</th>
            <th scope="col">{{ t("audit.colAction") }}</th>
            <th scope="col">{{ t("audit.colDoc") }}</th>
            <th scope="col">{{ t("audit.colTime") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(a, i) in items" :key="i" data-testid="audit-row">
            <td>{{ a.actor }}</td>
            <td>
              <span class="badge" :class="a.action === 'UPLOAD' ? 'badge-neutral' : 'badge-warning'">{{ M[`audit.${a.action}`] }}</span>
            </td>
            <td>{{ a.docName }}</td>
            <td>{{ formatDateTime(a.at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>
