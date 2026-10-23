import { ref } from "vue";
import { defineStore } from "pinia";

// Khung kho hội thoại (T-511). T-524 và T-512 bổ sung `messages`, `send`, `stop`, `open` đầy đủ.
export const useChatStore = defineStore("chat", () => {
  const sessionId = ref<string | null>(null);
  const draft = ref("");
  const busy = ref(false);
  const scope = ref<string[]>([]);
  const libraryEmpty = ref(false);

  function newSession(): void {
    sessionId.value = null;
    busy.value = false;
  }

  async function open(id: string): Promise<void> {
    sessionId.value = id;
  }

  return { sessionId, draft, busy, scope, libraryEmpty, newSession, open };
});
