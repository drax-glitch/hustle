import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("life_rpg_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getErrorMessage = (err, fallback = "Something went wrong") =>
  err?.response?.data?.error || fallback;

// ---- Auth ----
export const login = (payload) => api.post("/auth/login", payload).then((r) => r.data);
export const register = (payload) => api.post("/auth/register", payload).then((r) => r.data);
export const fetchMe = () => api.get("/auth/me").then((r) => r.data);

// ---- Dashboard ----
export const fetchDashboardStats = () => api.get("/dashboard/stats").then((r) => r.data);

// ---- Quests ----
export const fetchQuests = (params) => api.get("/quests", { params }).then((r) => r.data);
export const createQuest = (payload) => api.post("/quests", payload).then((r) => r.data);
export const updateQuest = (id, payload) => api.patch(`/quests/${id}`, payload).then((r) => r.data);
export const completeQuest = (id) => api.patch(`/quests/${id}/complete`).then((r) => r.data);
export const deleteQuest = (id) => api.delete(`/quests/${id}`).then((r) => r.data);

// ---- Character ----
export const fetchCharacter = () => api.get("/character").then((r) => r.data);

// ---- Achievements ----
export const fetchAchievements = () => api.get("/achievements").then((r) => r.data);

// ---- Shop ----
export const fetchShopItems = (params) => api.get("/shop", { params }).then((r) => r.data);
export const buyItem = (id) => api.post(`/shop/${id}/buy`).then((r) => r.data);
export const equipItem = (id) => api.post(`/shop/${id}/equip`).then((r) => r.data);
export const unequipItem = (id) => api.post(`/shop/${id}/unequip`).then((r) => r.data);

// ---- Progress ----
export const fetchProgress = () => api.get("/progress").then((r) => r.data);

// ---- Settings ----
export const updateSettings = (payload) => api.patch("/settings", payload).then((r) => r.data);
export const resetStreak = () => api.post("/settings/reset-streak").then((r) => r.data);
export const resetCharacter = () => api.post("/settings/reset-character").then((r) => r.data);
export const completeOnboarding = (lifeGoals) => api.post("/settings/complete-onboarding", { lifeGoals }).then((r) => r.data);

// ---- Skills ----
export const fetchSkills = () => api.get("/skills").then((r) => r.data);
export const unlockSkill = (id) => api.post(`/skills/${id}/unlock`).then((r) => r.data);

// ---- World ----
export const fetchWorld = () => api.get("/world").then((r) => r.data);
export const fetchRegion = (regionId) => api.get(`/world/regions/${regionId}`).then((r) => r.data);

// ---- Bosses ----
export const fetchBosses = () => api.get("/bosses").then((r) => r.data);
export const fetchBoss = (id) => api.get(`/bosses/${id}`).then((r) => r.data);
export const createBoss = (data) => api.post("/bosses", data).then((r) => r.data);
export const linkQuestToBoss = (bossId, questId) => api.post(`/bosses/${bossId}/quests`, { questId }).then((r) => r.data);
export const unlinkQuestFromBoss = (bossId, questId) => api.delete(`/bosses/${bossId}/quests/${questId}`).then((r) => r.data);
export const claimBossRewards = (bossId) => api.post(`/bosses/${bossId}/claim-rewards`).then((r) => r.data);

// ---- Game Master ----
export const fetchGameMasterAdvice = (refresh = false) =>
  api.get("/game-master/advice", { params: refresh ? { refresh: 1 } : {} }).then((r) => r.data);
export const fetchGameMasterBriefing = () => api.get("/game-master/briefing").then((r) => r.data);

// ---- Chronicle ----
export const fetchTodayChronicle = () => api.get("/chronicle/today").then((r) => r.data);
export const fetchChronicleHistory = (days = 30) => api.get("/chronicle/history", { params: { days } }).then((r) => r.data);
export const fetchChronicleByDate = (dateStr) => api.get(`/chronicle/date/${dateStr}`).then((r) => r.data);

// ---- Evolution ----
export const fetchEvolution = () => api.get("/character/evolution").then((r) => r.data);
export const ackEvolution = () => api.post("/character/evolution/ack").then((r) => r.data);

export default api;
