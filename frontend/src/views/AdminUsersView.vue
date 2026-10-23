<script setup lang="ts">
// S-07 Quản lý người dùng (allow-list), chỉ Quản trị viên (US-061, BR-016).
import { computed, onMounted, ref } from "vue";
import { ApiError, request } from "@/api/client";
import { messageFor } from "@/api/errors";
import type { Role, UserOut } from "@/api/types";
import AdminTabs from "@/components/AdminTabs.vue";
import ConfirmDialog from "@/components/ConfirmDialog.vue";
import SkeletonRows from "@/components/SkeletonRows.vue";
import { useToast } from "@/composables/useToast";
import { M, t } from "@/content/messages";
import { formatDateTime } from "@/utils/format";

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/; // cùng biểu thức với backend (T-110)
const ROLES: Role[] = ["BD_USER", "TEAM_LEAD", "ADMIN", "SPONSOR"];

const toast = useToast();
const items = ref<UserOut[]>([]);
const limit = ref(20);
const loading = ref(true);
const failed = ref(false);

const showForm = ref(false);
const email = ref("");
const role = ref<Role>("BD_USER");
const emailError = ref("");
const formError = ref("");
const submitting = ref(false);

const pendingRemove = ref<UserOut | null>(null);

const count = computed(() => items.value.length);

async function load() {
  loading.value = true;
  failed.value = false;
  try {
    const data = await request<{ items: UserOut[]; count: number; limit: number }>("/api/v1/admin/users");
    items.value = data.items;
    limit.value = data.limit;
  } catch {
    failed.value = true;
  } finally {
    loading.value = false;
  }
}

async function submit() {
  emailError.value = "";
  formError.value = "";
  const value = email.value.trim();
  if (!EMAIL_RE.test(value)) {
    emailError.value = messageFor("EMAIL_INVALID");
    return;
  }
  submitting.value = true;
  try {
    const created = await request<UserOut>("/api/v1/admin/users", { method: "POST", body: { email: value, role: role.value } });
    items.value.push(created);
    email.value = "";
    showForm.value = false;
  } catch (e) {
    const code = e instanceof ApiError ? e.code : "INTERNAL";
    if (code === "EMAIL_INVALID" || code === "USER_EXISTS") emailError.value = messageFor(code);
    else if (code === "USER_LIMIT_REACHED") formError.value = messageFor(code);
    else toast.show(messageFor(code), "error");
  } finally {
    submitting.value = false;
  }
}

async function confirmRemove() {
  const user = pendingRemove.value;
  pendingRemove.value = null;
  if (!user) return;
  try {
    await request<void>(`/api/v1/admin/users/${encodeURIComponent(user.email)}`, { method: "DELETE" });
    items.value = items.value.filter((u) => u.email !== user.email);
    toast.show(t("users.removed", { email: user.email }), "success");
  } catch (e) {
    toast.show(messageFor(e instanceof ApiError ? e.code : "INTERNAL"), "error");
  }
}

onMounted(load);
</script>

<template>
  <main id="main" class="page" data-testid="admin-users">
    <AdminTabs />
    <div class="page-head">
      <h1>
        {{ t("users.title") }}
        <span class="muted count" data-testid="user-count">({{ count }}/{{ limit }})</span>
      </h1>
      <button type="button" class="btn btn-primary" data-testid="open-add" :aria-expanded="showForm" @click="showForm = !showForm">
        {{ t("users.add") }}
      </button>
    </div>
    <p class="caption muted note">{{ t("users.note") }}</p>

    <form v-if="showForm" class="add-form" novalidate data-testid="add-form" @submit.prevent="submit">
      <p v-if="formError" class="field-error" role="alert" data-testid="form-error">{{ formError }}</p>
      <div class="field">
        <label for="new-user-email">{{ t("users.formEmail") }}</label>
        <input
          id="new-user-email"
          v-model="email"
          class="input"
          type="email"
          autocomplete="off"
          :aria-invalid="emailError ? 'true' : undefined"
          :aria-describedby="emailError ? 'new-user-email-error' : undefined"
          data-testid="email-input"
        />
        <p v-if="emailError" id="new-user-email-error" class="field-error" data-testid="email-error">{{ emailError }}</p>
      </div>
      <div class="field">
        <label for="new-user-role">{{ t("users.formRole") }}</label>
        <select id="new-user-role" v-model="role" class="select" data-testid="role-select">
          <option v-for="r in ROLES" :key="r" :value="r">{{ M[`role.${r}`] }}</option>
        </select>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="submitting" data-testid="submit-add">{{ t("users.formSubmit") }}</button>
    </form>

    <SkeletonRows v-if="loading" :rows="3" />
    <div v-else-if="failed" class="state-box is-error" role="alert" data-testid="load-error">
      <strong>{{ t("users.loadError") }}</strong>
      <button type="button" class="btn" data-testid="retry" @click="load">{{ t("action.retry") }}</button>
    </div>
    <div v-else-if="items.length === 0" class="state-box" data-testid="empty">
      <strong>{{ t("users.empty") }}</strong>
      <button type="button" class="btn btn-primary" @click="showForm = true">{{ t("users.add") }}</button>
    </div>
    <div v-else class="table-wrap">
      <table class="table" data-testid="user-table">
        <caption class="sr-only">{{ t("users.caption") }}</caption>
        <thead>
          <tr>
            <th scope="col">{{ t("users.colEmail") }}</th>
            <th scope="col">{{ t("users.colRole") }}</th>
            <th scope="col">{{ t("users.colAddedAt") }}</th>
            <th scope="col"><span class="sr-only">{{ t("users.colActions") }}</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in items" :key="u.email" data-testid="user-row">
            <td>{{ u.email }}</td>
            <td>{{ M[`role.${u.role}`] }}</td>
            <td>{{ formatDateTime(u.addedAt) }}</td>
            <td>
              <button
                type="button"
                class="btn btn-ghost btn-sm danger-text"
                :aria-label="t('users.removeAria', { email: u.email })"
                data-testid="remove"
                @click="pendingRemove = u"
              >
                {{ t("users.remove") }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmDialog
      :open="pendingRemove !== null"
      :title="pendingRemove ? t('users.removeTitle', { email: pendingRemove.email }) : ''"
      :confirm-label="t('users.removeConfirm')"
      destructive
      @confirm="confirmRemove"
      @cancel="pendingRemove = null"
    >
      {{ pendingRemove ? t("users.removeBody", { email: pendingRemove.email }) : "" }}
    </ConfirmDialog>
  </main>
</template>

<style scoped>
.count {
  font-weight: 400;
}
.note {
  margin-bottom: var(--space-4);
}
.add-form {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: var(--space-4);
  padding: var(--space-4);
  margin-bottom: var(--space-5);
  background: var(--color-surface);
  border-radius: var(--radius-card);
}
.add-form .field {
  min-width: 240px;
}
.add-form > .btn {
  align-self: flex-end;
}
.add-form > .field-error {
  flex-basis: 100%;
}
.danger-text {
  color: var(--color-danger-text);
}
</style>
