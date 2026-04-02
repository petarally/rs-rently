import axios from "axios";

const API_BASE_URL = "http://localhost";

const authAPI = axios.create({
  baseURL: `${API_BASE_URL}:8000`,
});

const bookingAPI = axios.create({
  baseURL: `${API_BASE_URL}:8001`,
});

const damageAPI = axios.create({
  baseURL: `${API_BASE_URL}:8002`,
});

const addAuthToken = (config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

bookingAPI.interceptors.request.use(addAuthToken);
damageAPI.interceptors.request.use(addAuthToken);
// Basic response error interceptor to normalize/log errors
const handleError = (error) => {
  console.error("API error:", error);
  return Promise.reject(error);
};

authAPI.interceptors.response.use((r) => r, handleError);
bookingAPI.interceptors.response.use((r) => r, handleError);
damageAPI.interceptors.response.use((r) => r, handleError);

export default {
  login(username, password) {
    return authAPI.post("/login", { username, password });
  },

  verifyToken(token) {
    return authAPI.get("/verify", { params: { token } });
  },

  createBooking(carId, userEmail) {
    return bookingAPI.post("/bookings", null, {
      params: { car_id: carId, user_email: userEmail },
    });
  },

  uploadDamage(file) {
    const formData = new FormData();
    formData.append("file", file);
    return damageAPI.post("/upload-damage", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
};
