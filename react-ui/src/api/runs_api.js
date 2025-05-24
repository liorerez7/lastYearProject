// react-ui/src/api/runs_api.js
import axios from "axios";
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8080";

export const getRuns = () => axios.get(`${API_URL}/runs`).then(r => r.data);
export const getRun = async (id) => {
  const res = await axios.get(`${API_URL}/runs/${id}`);
  const data = res.data;

  return {
    plan_name: data.plan_name,
    started_at: data.started_at,
    finished_at: data.finished_at,
    status: data.status,
    cloud_provider: data.cloud_provider,
    source_db: data.source_db,
    destination_db: data.destination_db,
    id: data.id
  };
};
