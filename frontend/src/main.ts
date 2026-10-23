import { createApp } from "vue";
import { createPinia } from "pinia";
import "./styles/tokens.css";
import "./styles/base.css";
import App from "./App.vue";
import router from "./router";
import { installGuards } from "./router/guards";

const pinia = createPinia();
const app = createApp(App).use(pinia);
installGuards(router);
app.use(router).mount("#app");
