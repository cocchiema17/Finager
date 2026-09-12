import axios from "axios";

// Assicura l'invio automatico dei cookie HTTP-only di sessione
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
}

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
    pageSize
  }

  Object.entries(filters).forEach(e => {
    if (e[1] && e[1] != "") {
      query[e[0]] = e[1];
    }
  });

  if (sortColumn) {
    query.sortColumn = sortColumn;
  }


  if (typeof asc == 'boolean') {
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
  return axios.delete(`/api/transactions/${id}`, id);
}

const updateTransaction = (id, payload) => {
  return axios.patch(`/api/transactions/${id}`, payload)
}

const createSpace = async (name) => {
  const { data } = await axios.post("/api/spaces", { name });
  return data;
};

const getExcelReport = async () => {
  const { data } = await axios.get('/api/report', { responseType: 'arraybuffer' });
  return data;
}

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
  getExcelReport
};
