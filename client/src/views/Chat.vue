<template>
  <div class="chat-page bg-app">
    <div class="container-fluid h-100 py-3">
      <div class="row h-100 g-3">
        <!-- SIDEBAR SESSIONI -->
        <div class="col-12 col-md-4 col-lg-3 d-flex flex-column h-100">
          <div class="card shadow-sm border-0 flex-grow-1 d-flex flex-column overflow-hidden">
            <div class="card-header bg-white border-bottom py-3">
              <button
                @click="handleNewSession"
                class="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-2"
                :disabled="isStreaming"
              >
                <i class="bi bi-plus-lg"></i>
                <span>Nuova Conversazione</span>
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
          <div class="card shadow-sm border-0 flex-grow-1 d-flex flex-column overflow-hidden">
            <!-- Header Chat -->
            <div class="card-header bg-white border-bottom py-3 d-flex align-items-center justify-content-between">
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-primary-subtle text-primary p-2 rounded-circle">
                  <i class="bi bi-robot fs-5"></i>
                </span>
                <div>
                  <h6 class="mb-0 fw-semibold">
                    {{ currentSession ? currentSession.title : "Finager AI Assistant" }}
                  </h6>
                  <small class="text-muted">Assistente personale per la gestione finanziaria</small>
                </div>
              </div>
              <span v-if="isStreaming" class="badge bg-info-subtle text-info">
                <span class="spinner-grow spinner-grow-sm me-1" role="status"></span>
                Sta scrivendo...
              </span>
            </div>

            <!-- Contenitore Messaggi -->
            <div ref="messagesContainer" class="card-body overflow-auto p-4 messages-area">
              <!-- Empty State / Benvenuto -->
              <div
                v-if="!currentSession || currentSession.messages.length === 0"
                class="h-100 d-flex flex-column align-items-center justify-content-center text-center px-3"
              >
                <div class="bg-primary-subtle text-primary rounded-circle p-3 mb-3">
                  <i class="bi bi-stars fs-1"></i>
                </div>
                <h5 class="fw-semibold">Ciao{{ user ? `, ${user.firstName}` : "" }}! Come posso aiutarti oggi?</h5>
                <p class="text-muted max-w-500 mb-4">
                  Chiedimi consigli su come ottimizzare il budget mensile, ridurre le spese ricorrenti o pianificare i tuoi risparmi.
                </p>

                <div class="d-flex flex-wrap justify-content-center gap-2">
                  <button
                    v-for="(suggestion, idx) in quickPrompts"
                    :key="idx"
                    @click="useSuggestion(suggestion)"
                    class="btn btn-outline-primary btn-sm rounded-pill px-3"
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
                    <div class="message-text">{{ msg.content }}<span v-if="isStreaming && index === currentSession.messages.length - 1 && msg.role === 'assistant'" class="typing-cursor">|</span></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Form Input Messaggio -->
            <div class="card-footer bg-white border-top p-3">
              <form @submit.prevent="sendMessage" class="d-flex gap-2 align-items-end">
                <textarea
                  v-model="promptInput"
                  @keydown.enter.exact.prevent="sendMessage"
                  class="form-control resize-none"
                  rows="1"
                  placeholder="Scrivi una domanda sull'andamento delle tue spese... (Invio per inviare)"
                  :disabled="isStreaming"
                ></textarea>
                <button
                  type="submit"
                  class="btn btn-primary px-4 py-2 d-flex align-items-center gap-2"
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
        await this.fetchSessions();
      } catch (err) {
        this.newToast("Impossibile creare una nuova chat", TYPE.ERROR);
      }
    },

    async selectSession(sessionId) {
      if (this.isStreaming) return;
      try {
        this.currentSession = await getChatSession(sessionId);
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

      // Se non c'è una sessione selezionata, creala automaticamente al primo invio
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

      // Aggiunge subito il messaggio utente e il placeholder per l'assistente
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
          // Aggiorna la sidebar (titolo automatico e timestamp)
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

.message-bubble {
  max-width: 78%;
  word-wrap: break-word;
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