// react-ui/src/state/queries.js
import { useQuery } from "react-query";
import { getRuns, getRun } from "../api/runs_api";

export const useRunsList = () =>
  useQuery("runs", getRuns, { staleTime: 30000, refetchInterval: 60000 });

export const useRunDetails = id =>
  useQuery(["run", id], () => getRun(id), {
    staleTime: 10000,
    refetchInterval: data =>
      data && ["pending", "running"].includes(data.status) ? 5000 : false,
  });
