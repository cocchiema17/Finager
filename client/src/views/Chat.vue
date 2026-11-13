<template>
  <div class="chat-page bg-app">
    <div class="container-fluid h-100 p-0 p-md-3">
      <div class="row h-100 g-0 g-md-3 position-relative">
        <!-- BACKDROP MOBILE QUANDO IL DRAWER È APERTO -->
        <div
          v-if="showMobileSidebar"
          @click="showMobileSidebar = false"
          class="mobile-backdrop d-md-none"
        ></div>

        <!-- SIDEBAR SESSIONI (Fissa su Desktop, Drawer scorrevole su Mobile) -->
        <div
          class="col-md-4 col-lg-3 h-100 sidebar-wrapper"
          :class="{ 'sidebar-open': showMobileSidebar }"
        >
          <div class="card shadow-sm border-0 h-100 d-flex flex-column rounded-0 rounded-md-3 overflow-hidden">
            <div class="card-header bg-white border-bottom py-3 d-flex align-items-center justify-content-between gap-2">
              <button
                @click="handleNewSession"
                class="btn btn-primary flex-grow-1 d-flex align-items-center justify-content-center gap-2"
                :disabled="isStreaming"
              >
                <i class="bi bi-plus-lg"></i>
                <span>Nuova Chat</span>
              </button>
              <button
                @click="showMobileSidebar = false"
                class="btn btn-outline-secondary d-md-none"
                aria-label="Chiudi elenco chat"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>

            <div class="card-body p-2 overflow-auto flex-grow-1">
              <div v-if="loadingSessions" class="text-center py-4 text-muted">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <div class="small mt-2">Caricamento chat...</div>
              </div>

              <div v-else-if="sessions.length === 0" class="text-center py-5 text-muted px-3">
                <i class="bi bi-chat-square-text fs-2 d-block mb-2"></i>
                <p class="small mb-0">Nessuna conversazione salvata. Inizia una nuova chat!</p>
              </div>

              <div v-else class="list-group list-group-flush">
                <div
                  v-for="session in sessions"
                  :key="session.id"
                  @click="selectSession(session.id)"
                  class="list-group-item list-group-item-action border-0 rounded-2 mb-1 d-flex justify-content-between align-items-center session-item"
                  :class="{ 'active-session': currentSession && currentSession.id === session.id }"
                >
                  <div class="text-truncate me-2">
                    <div class="fw-medium text-truncate small">
                      <i class="bi bi-chat-left-text me-2"></i>{{ session.title }}
                    </div>
                    <div class="text-muted extra-small">
                      {{ formatDate(session.updatedAt) }}
                    </div>
                  </div>
                  <button
                    @click.stop="handleDeleteSession(session.id)"
                    class="btn btn-sm btn-link text-danger p-1 delete-btn"
                    title="Elimina conversazione"
                    :disabled="isStreaming"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AREA MESSAGGI PRINCIPALE -->
        <div class="col-12 col-md-8 col-lg-9 d-flex flex-column h-100">
          <div class="card shadow-sm border-0 flex-grow-1 d-flex flex-column rounded-0 rounded-md-3 overflow-hidden">
            <!-- Header Chat -->
            <div class="card-header bg-white border-bottom py-2 py-md-3 px-3 d-flex align-items-center justify-content-between gap-2">
              <div class="d-flex align-items-center gap-2 text-truncate">
                <!-- Pulsante apertura storico su Mobile -->
                <button
                  @click="showMobileSidebar = true"
                  class="btn btn-outline-secondary btn-sm d-md-none flex-shrink-0"
                  title="Storico conversazioni"
                >
                  <i class="bi bi-list fs-5"></i>
                </button>

                <span class="badge bg-primary-subtle text-primary p-2 rounded-circle flex-shrink-0">
                  <i class="bi bi-robot fs-5"></i>
                </span>
                <div class="text-truncate">
                  <h6 class="mb-0 fw-semibold text-truncate">
                    {{ currentSession ? currentSession.title : "Finager AI Assistant" }}
                  </h6>
                  <small class="text-muted d-none d-sm-block">
                    Assistente personale per la gestione finanziaria
                  </small>
                </div>
              </div>

              <div class="d-flex align-items-center gap-2 flex-shrink-0">
                <span v-if="isStreaming" class="badge bg-info-subtle text-info">
                  <span class="spinner-grow spinner-grow-sm me-1" role="status"></span>
                  <span class="d-none d-sm-inline">Sta scrivendo...</span>
                </span>
                <button
                  @click="handleNewSession"
                  class="btn btn-outline-primary btn-sm d-md-none"
                  title="Nuova chat"
                  :disabled="isStreaming"
                >
                  <i class="bi bi-plus-lg"></i>
                </button>
              </div>
            </div>

            <!-- Contenitore Messaggi -->
            <div ref="messagesContainer" class="card-body overflow-auto p-3 p-md-4 messages-area">
              <!-- Empty State / Benvenuto -->
              <div
                v-if="!currentSession || currentSession.messages.length === 0"
                class="h-100 d-flex flex-column align-items-center justify-content-center text-center px-2 px-md-3"
              >
                <div class="bg-primary-subtle text-primary rounded-circle p-3 mb-3">
                  <i class="bi bi-stars fs-1"></i>
                </div>
                <h5 class="fw-semibold">Ciao{{ user ? `, ${user.firstName}` : "" }}! Come posso aiutarti oggi?</h5>
                <p class="text-muted max-w-500 small mb-4">
                  Chiedimi consigli su come ottimizzare il budget mensile, ridurre le spese ricorrenti o pianificare i tuoi risparmi.
                </p>

                <div class="d-flex flex-column flex-sm-row flex-wrap justify-content-center gap-2 w-100 max-w-600">
                  <button
                    v-for="(suggestion, idx) in quickPrompts"
                    :key="idx"
                    @click="useSuggestion(suggestion)"
                    class="btn btn-outline-primary btn-sm rounded-pill px-3 text-wrap"
                  >
                    {{ suggestion }}
                  </button>
                </div>
              </div>

              <!-- Lista Messaggi -->
              <div v-else class="d-flex flex-column gap-3">
                <div
                  v-for="(msg, index) in currentSession.messages"
                  :key="index"
                  class="d-flex"
                  :class="msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'"
                >
                  <div
                    class="message-bubble p-3 rounded-3 shadow-sm"
                    :class="
                      msg.role === 'user'
                        ? 'bg-primary text-white user-bubble'
                        : 'bg-white border assistant-bubble'
                    "
                  >
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <small class="fw-semibold opacity-75">
                        {{ msg.role === "user" ? "Tu" : "Finager AI" }}
                      </small>
                    </div>
                    <div class="message-text">
                      {{ msg.content }}<span
                        v-if="isStreaming && index === currentSession.messages.length - 1 && msg.role === 'assistant'"
                        class="typing-cursor"
                      >|</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Form Input Messaggio -->
            <div class="card-footer bg-white border-top p-2 p-md-3">
              <form @submit.prevent="sendMessage" class="d-flex gap-2 align-items-end">
                <textarea
                  v-model="promptInput"
                  @keydown.enter.exact.prevent="sendMessage"
                  class="form-control resize-none"
                  rows="1"
                  placeholder="Scrivi una domanda... (Invio per inviare)"
                  :disabled="isStreaming"
                ></textarea>
                <button
                  type="submit"
                  class="btn btn-primary px-3 px-md-4 py-2 d-flex align-items-center gap-2 flex-shrink-0"
                  :disabled="!promptInput.trim() || isStreaming"
                >
                  <i class="bi bi-send-fill"></i>
                  <span class="d-none d-sm-inline">Invia</span>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { TYPE } from "vue-toastification";
import {
  getChatSessions,
  createChatSession,
  getChatSession,
  deleteChatSession,
  streamChatMessage,
} from "../api";

export default {
  name: "ChatView",
  data() {
    return {
      sessions: [],
      currentSession: null,
      promptInput: "",
      loadingSessions: false,
      isStreaming: false,
      showMobileSidebar: false,
      quickPrompts: [
        "Come posso applicare la regola del 50/30/20 al mio stipendio?",
        "Dammi 5 consigli pratici per ridurre le spese fisse mensili",
        "Come creare un fondo di emergenza efficace?",
      ],
    };
  },
  computed: {
    ...mapGetters(["user"]),
  },
  async mounted() {
    await this.fetchSessions();
  },
  methods: {
    async fetchSessions() {
      this.loadingSessions = true;
      try {
        this.sessions = await getChatSessions();
        if (this.sessions.length > 0 && !this.currentSession) {
          await this.selectSession(this.sessions[0].id);
        }
      } catch (err) {
        this.newToast("Errore nel caricamento delle conversazioni", TYPE.ERROR);
      } finally {
        this.loadingSessions = false;
      }
    },

    async handleNewSession() {
      try {
        const created = await createChatSession("Nuova conversazione");
        this.currentSession = created;
        this.showMobileSidebar = false;
        await this.fetchSessions();
      } catch (err) {
        this.newToast("Impossibile creare una nuova chat", TYPE.ERROR);
      }
    },

    async selectSession(sessionId) {
      if (this.isStreaming) return;
      try {
        this.currentSession = await getChatSession(sessionId);
        this.showMobileSidebar = false;
        this.scrollToBottom();
      } catch (err) {
        this.newToast("Errore nel recupero della sessione", TYPE.ERROR);
      }
    },

    async handleDeleteSession(sessionId) {
      try {
        await deleteChatSession(sessionId);
        if (this.currentSession && this.currentSession.id === sessionId) {
          this.currentSession = null;
        }
        await this.fetchSessions();
        this.newToast("Conversazione eliminata", TYPE.INFO);
      } catch (err) {
        this.newToast("Errore durante l'eliminazione", TYPE.ERROR);
      }
    },

    useSuggestion(text) {
      this.promptInput = text;
      this.sendMessage();
    },

    async sendMessage() {
      const text = this.promptInput.trim();
      if (!text || this.isStreaming) return;

      this.promptInput = "";

      if (!this.currentSession) {
        try {
          this.currentSession = await createChatSession(text.slice(0, 40));
          this.sessions.unshift({
            id: this.currentSession.id,
            title: this.currentSession.title,
            updatedAt: new Date().toISOString(),
          });
        } catch (err) {
          this.newToast("Errore nella creazione della sessione", TYPE.ERROR);
          return;
        }
      }

      this.currentSession.messages.push({
        role: "user",
        content: text,
      });

      const assistantMsg = {
        role: "assistant",
        content: "",
      };
      this.currentSession.messages.push(assistantMsg);
      const assistantIdx = this.currentSession.messages.length - 1;

      this.isStreaming = true;
      this.scrollToBottom();

      await streamChatMessage(this.currentSession.id, text, {
        onChunk: (token) => {
          this.currentSession.messages[assistantIdx].content += token;
          this.scrollToBottom();
        },
        onDone: async () => {
          this.isStreaming = false;
          this.scrollToBottom();
          const updatedList = await getChatSessions();
          this.sessions = updatedList;
        },
        onError: (errMsg) => {
          this.isStreaming = false;
          this.newToast(errMsg, TYPE.ERROR);
          if (!this.currentSession.messages[assistantIdx].content) {
            this.currentSession.messages[assistantIdx].content =
              "⚠️ Si è verificato un errore durante la generazione della risposta.";
          }
        },
      });
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer;
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    },

    formatDate(isoString) {
      if (!isoString) return "";
      const date = new Date(isoString);
      return date.toLocaleDateString("it-IT", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
  },
};
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 57px);
  height: calc(100dvh - 57px);
  overflow: hidden;
}

.session-item {
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.session-item:hover {
  background-color: #f0f4f8;
}

.active-session {
  background-color: #e7f1ff !important;
  color: #0d6efd;
}

.extra-small {
  font-size: 0.75rem;
}

.max-w-500 {
  max-width: 500px;
}

.max-w-600 {
  max-width: 600px;
}

/* Adattamento fumetti messaggi su Mobile e Desktop */
.message-bubble {
  max-width: 88%;
  word-wrap: break-word;
}

@media (min-width: 768px) {
  .message-bubble {
    max-width: 76%;
  }

  .rounded-md-3 {
    border-radius: 0.5rem !important;
  }
}

/* Comportamento Drawer della Sidebar su schermi < 768px */
@media (max-width: 767.98px) {
  .sidebar-wrapper {
    position: fixed;
    top: 57px;
    left: 0;
    bottom: 0;
    width: 285px;
    max-width: 82vw;
    z-index: 1045;
    transform: translateX(-100%);
    transition: transform 0.25s ease-in-out;
  }

  .sidebar-wrapper.sidebar-open {
    transform: translateX(0);
  }

  .mobile-backdrop {
    position: fixed;
    top: 57px;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.45);
    z-index: 1040;
  }
}

.message-text {
  white-space: pre-wrap;
  line-height: 1.5;
}

.resize-none {
  resize: none;
}

.typing-cursor {
  display: inline-block;
  margin-left: 2px;
  font-weight: bold;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>