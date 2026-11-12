import axios from "axios";

axios.defaults.withCredentials = true;

axios.interceptors.request.use(
  (config) => {
    const csrfToken = localStorage.getItem("csrfToken");
    if (csrfToken) {
      config.headers["x-csrf-token"] = csrfToken;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const getChartsData = (spaceId, fromDate, toDate) => {
  const params = { spaceId };

  if (fromDate) params.fromDate = fromDate;
  if (toDate) params.toDate = toDate;

  return axios.get("/api/charts", { params });
};

const logout = () => {
  return axios.post("/api/auth/logout");
};

const login = async (email, password) => {
  const { data } = await axios.post("/api/auth/signin", { email, password });
  return data;
};

const getCurrentUser = async () => {
  const { data } = await axios.get("/api/auth/currentUser");
  return data;
};

const getSpaces = async () => {
  const { data } = await axios.get("/api/spaces");
  return data.value;
};

const getCategories = async () => {
  const { data } = await axios.get("/api/categories");
  return data.value;
};

const getTransactions = async (page = 0, pageSize = 10, filters = {}, sortColumn, asc) => {
  const query = {
    page,
    pageSize,
  };

  Object.entries(filters).forEach((e) => {
    if (e[1] && e[1] !== "") {
      query[e[0]] = e[1];
    }
  });

  if (sortColumn) {
    query.sortColumn = sortColumn;
  }

  if (typeof asc === "boolean") {
    query.asc = asc;
  }

  const { data } = await axios.get("/api/transactions", {
    params: query,
  });
  return data;
};

const createTransaction = async (payload) => {
  const { data } = await axios.post("/api/transactions", payload);
  return data;
};

const deleteTransaction = (id) => {
  return axios.delete(`/api/transactions/${id}`);
};

const updateTransaction = (id, payload) => {
  return axios.patch(`/api/transactions/${id}`, payload);
};

const createSpace = async (name) => {
  const { data } = await axios.post("/api/spaces", { name });
  return data;
};

const getExcelReport = async () => {
  const { data } = await axios.get("/api/report", { responseType: "arraybuffer" });
  return data;
};

// --- CHAT & LLM (MongoDB + Ollama SSE) ---

const getChatSessions = async () => {
  const { data } = await axios.get("/api/chat/sessions");
  return data;
};

const createChatSession = async (title = "Nuova conversazione") => {
  const { data } = await axios.post("/api/chat/sessions", { title });
  return data;
};

const getChatSession = async (sessionId) => {
  const { data } = await axios.get(`/api/chat/sessions/${sessionId}`);
  return data;
};

const deleteChatSession = async (sessionId) => {
  await axios.delete(`/api/chat/sessions/${sessionId}`);
};

/**
 * Invia un messaggio e legge in tempo reale lo stream SSE da Ollama.
 * @param {string} sessionId
 * @param {string} message
 * @param {(chunkText: string) => void} onChunk - Callback invocata per ogni nuovo token
 * @param {() => void} onDone - Callback invocata al completamento
 * @param {(errorMsg: string) => void} onError - Callback in caso di errore
 */
const streamChatMessage = async (sessionId, message, { onChunk, onDone, onError }) => {
  try {
    const response = await fetch(`/api/chat/sessions/${sessionId}/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Errore HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";
    let doneCalled = false;
    let isReading = true;

    while (isReading) {
      const { value, done } = await reader.read();
      if (done) {
        isReading = false;
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("data:")) continue;

        const jsonStr = trimmed.replace(/^data:\s*/, "");
        try {
          const parsed = JSON.parse(jsonStr);
          if (parsed.error) {
            if (onError) onError(parsed.error);
            return;
          }
          if (parsed.content && onChunk) {
            onChunk(parsed.content);
          }
          if (parsed.done) {
            doneCalled = true;
            if (onDone) onDone();
            return;
          }
        } catch (e) {
          // Ignora chunk JSON parziali
        }
      }
    }

    if (!doneCalled && onDone) onDone();
  } catch (err) {
    if (onError) onError(err.message || "Errore di connessione con il server AI");
  }
};

export {
  getCurrentUser,
  getSpaces,
  getCategories,
  getTransactions,
  login,
  logout,
  createTransaction,
  deleteTransaction,
  updateTransaction,
  createSpace,
  getChartsData,
  getExcelReport,
  getChatSessions,
  createChatSession,
  getChatSession,
  deleteChatSession,
  streamChatMessage,
};