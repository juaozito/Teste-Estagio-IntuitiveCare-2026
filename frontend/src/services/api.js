import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 5000 // 5 segundos de limite
});

export default api;