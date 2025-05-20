// react-ui/src/api/runs_api.js
import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";

export const getRuns = () => axios.get(`${API_URL}/runs`).then(r => r.data);
export const getRun  = id => axios.get(`${API_URL}/runs/${id}`).then(r => r.data);
