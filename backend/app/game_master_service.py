"""AI Game Master — guidance only. Never mutates XP, gold, attributes, or bosses."""
import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

from app.config import Config
from app.rpg_utils import REGIONS

VALID_PRIORITIES = {"high", "medium", "low"}
VALID_REGIONS = {info["name"] for info in REGIONS.values()} | {rid.capitalize() for rid in REGIONS}
CACHE_TTL_SECONDS = 600
_advice_cache: Dict[int, Dict[str, Any]] = {}


def _safe_text(value, limit=500) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text[:limit]


class GameMasterService:
    """Personalized RPG guide. Backend remains source of truth; AI only narrates."""

    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.api_key = Config.AI_API_KEY
        self.model = Config.AI_MODEL
        self.timeout = Config.AI_TIMEOUT

    def is_available(self) -> bool:
        return bool(self.api_key) and self.provider not in ("mock", "", None)

    def generate_advice(self, user_state: Dict[str, Any], use_cache: bool = True) -> Dict[str, Any]:
        user_id = user_state.get("user_id")
        if use_cache and user_id is not None:
            cached = _advice_cache.get(user_id)
            if cached and (time.time() - cached["ts"] < CACHE_TTL_SECONDS):
                return cached["advice"]

        fallback = self._generate_fallback_advice(user_state)
        if not self.is_available():
            result = {**fallback, "source": "fallback"}
            self._store_cache(user_id, result)
            return result

        try:
            raw = self._call_provider(user_state)
            parsed = self._parse_ai_response(raw, user_state)
            validated = self.validate_advice(parsed, user_state)
            validated["source"] = "ai"
            self._store_cache(user_id, validated)
            return validated
        except Exception:
            result = {**fallback, "source": "fallback"}
            self._store_cache(user_id, result)
            return result

    def generate_briefing(self, user_state: Dict[str, Any], advice: Dict[str, Any]) -> Dict[str, Any]:
        signals = user_state.get("signals") or self.compute_signals(user_state)
        strongest = signals.get("strongest_region") or {}
        weakest = signals.get("weakest_region") or {}
        bonus_region = weakest.get("name") if weakest.get("name") != (advice.get("region") or "") else strongest.get("name")

        briefing = {
            "greeting": "Good morning, Adventurer." if not user_state.get("display_name") else f"Good morning, {user_state['display_name']}.",
            "strongest_region": strongest.get("name"),
            "weakest_region": weakest.get("name"),
            "recommended_mission": advice.get("recommended_action"),
            "why": advice.get("reason"),
            "bonus_objective": f"Complete one {bonus_region} quest." if bonus_region else "Complete one extra quest today.",
            "quest_id": advice.get("quest_id"),
            "boss_id": advice.get("boss_id"),
            "region": advice.get("region"),
            "action_path": advice.get("action_path"),
        }

        if self.is_available():
            try:
                prompt = (
                    "Write a 1-sentence RPG daily briefing greeting based on this state. "
                    "JSON only: {\"greeting\": \"...\"}. No secrets.\n"
                    f"Class: {user_state.get('class')}, Level: {user_state.get('level')}, "
                    f"Strongest: {strongest.get('name')}, Weakest: {weakest.get('name')}."
                )
                raw = self._http_chat(
                    "You write short RPG briefing greetings. Return JSON only.",
                    prompt,
                )
                data = json.loads(self._extract_json(raw))
                if data.get("greeting"):
                    briefing["greeting"] = _safe_text(data["greeting"], 180)
            except Exception:
                pass
        return briefing

    @staticmethod
    def compute_signals(user_state: Dict[str, Any]) -> Dict[str, Any]:
        region_progress = user_state.get("region_progress") or {}
        named = []
        for region_id, pct in region_progress.items():
            info = REGIONS.get(str(region_id).lower(), {})
            named.append({
                "id": str(region_id).lower(),
                "name": info.get("name", str(region_id).capitalize()),
                "progress": int(pct or 0),
                "category": info.get("category"),
            })
        weakest = min(named, key=lambda r: r["progress"]) if named else None
        strongest = max(named, key=lambda r: r["progress"]) if named else None
        active_boss = user_state.get("active_boss")
        unfinished = user_state.get("unfinished_quests") or []
        return {
            "weakest_region": weakest,
            "strongest_region": strongest,
            "active_boss": active_boss,
            "boss_progress": (100 - active_boss.get("hp_percent", 100)) if active_boss else 0,
            "current_streak": user_state.get("streak", 0),
            "recent_activity": user_state.get("recent_activity", 0),
            "unused_skill_points": user_state.get("skill_points", 0),
            "unfinished_quests": len(unfinished),
            "recommended_skill": user_state.get("recommended_skill"),
        }

    def _generate_fallback_advice(self, user_state: Dict[str, Any]) -> Dict[str, Any]:
        signals = user_state.get("signals") or self.compute_signals(user_state)
        unfinished = user_state.get("unfinished_quests") or []
        skill_points = user_state.get("skill_points", 0)
        active_boss = user_state.get("active_boss")
        recommended_skill = user_state.get("recommended_skill")
        weakest = signals.get("weakest_region") or {}
        strongest = signals.get("strongest_region") or {}

        linked_quest = None
        if active_boss:
            for q in unfinished:
                if q.get("id") in (active_boss.get("linked_quest_ids") or []) or q.get("category") == active_boss.get("category"):
                    linked_quest = q
                    break

        if active_boss and active_boss.get("hp_percent", 100) <= 35:
            quest = linked_quest or (unfinished[0] if unfinished else None)
            return self.validate_advice({
                "message": (
                    f"The {active_boss.get('title', 'active boss')} is weakening at "
                    f"{active_boss.get('hp_percent', 0)}% HP. One focused quest could finish this battle."
                ),
                "priority": "high",
                "recommended_action": f"Complete {quest['title']}" if quest else "Enter the boss battle",
                "region": active_boss.get("region_name") or active_boss.get("category"),
                "boss_id": active_boss.get("id"),
                "quest_id": quest.get("id") if quest else None,
                "reason": "Boss HP is critical. Completing a linked quest deals damage.",
            }, user_state)

        if skill_points > 0:
            skill_name = recommended_skill.get("name") if recommended_skill else "an available upgrade"
            return self.validate_advice({
                "message": (
                    f"You have {skill_points} unused Skill Point"
                    f"{'s' if skill_points != 1 else ''}. "
                    f"Recommended: unlock {skill_name}."
                ),
                "priority": "medium",
                "recommended_action": f"Unlock {skill_name}" if recommended_skill else "Visit the Skills tree",
                "region": None,
                "boss_id": None,
                "quest_id": None,
                "skill_id": recommended_skill.get("id") if recommended_skill else None,
                "reason": "Skill points do not spend themselves. Choose an upgrade — the Game Master will not unlock it for you.",
            }, user_state)

        weakest_pct = weakest.get("progress", 100)
        if weakest and weakest_pct < 40:
            matching = [q for q in unfinished if q.get("category") == weakest.get("category")]
            quest = matching[0] if matching else (unfinished[0] if unfinished else None)
            return self.validate_advice({
                "message": (
                    f"Your {weakest.get('name')} territory has fallen behind at {weakest_pct}%. "
                    f"{strongest.get('name') + ' is currently your strongest region.' if strongest else ''}"
                ).strip(),
                "priority": "medium",
                "recommended_action": f"Complete {quest['title']}" if quest else f"Start a {weakest.get('name')} quest",
                "region": weakest.get("name"),
                "boss_id": None,
                "quest_id": quest.get("id") if quest else None,
                "reason": f"{weakest.get('name')} needs attention to keep your world balanced.",
            }, user_state)

        if unfinished:
            quest = unfinished[0]
            return self.validate_advice({
                "message": f"Your strongest available move today: complete “{quest.get('title')}”.",
                "priority": "low",
                "recommended_action": f"Complete {quest.get('title')}",
                "region": quest.get("region_name") or quest.get("category"),
                "boss_id": active_boss.get("id") if active_boss else None,
                "quest_id": quest.get("id"),
                "reason": (
                    f"Reward: +{quest.get('xp_reward', 0)} XP"
                    + (f", boss damage toward {active_boss.get('title')}" if active_boss else "")
                ),
            }, user_state)

        return self.validate_advice({
            "message": "Choose a quest today to strengthen your character and world.",
            "priority": "low",
            "recommended_action": "View your quests",
            "region": weakest.get("name") if weakest else None,
            "boss_id": None,
            "quest_id": None,
            "reason": "Daily progress is the foundation of adventure.",
        }, user_state)

    def validate_advice(self, advice: Dict[str, Any], user_state: Dict[str, Any]) -> Dict[str, Any]:
        """Treat AI output as untrusted. Only keep IDs that exist for this user."""
        unfinished = {q.get("id"): q for q in (user_state.get("unfinished_quests") or [])}
        active_boss = user_state.get("active_boss")
        recommended_skill = user_state.get("recommended_skill")

        region_lookup = {}
        for info in REGIONS.values():
            region_lookup[info["name"].lower()] = info["name"]
            region_lookup[info["id"]] = info["name"]

        quest_id = None
        try:
            candidate = int(advice["quest_id"]) if advice.get("quest_id") is not None else None
            if candidate in unfinished:
                quest_id = candidate
        except (TypeError, ValueError):
            quest_id = None

        boss_id = None
        if active_boss and advice.get("boss_id") is not None:
            try:
                if int(advice.get("boss_id")) == int(active_boss.get("id")):
                    boss_id = active_boss.get("id")
            except (TypeError, ValueError):
                boss_id = None

        skill_id = None
        if recommended_skill and advice.get("skill_id") is not None:
            try:
                if int(advice.get("skill_id")) == int(recommended_skill.get("id")):
                    skill_id = recommended_skill.get("id")
            except (TypeError, ValueError):
                skill_id = None

        raw_region = advice.get("region")
        region = None
        if raw_region:
            region = region_lookup.get(str(raw_region).lower()) or region_lookup.get(str(raw_region))

        priority = str(advice.get("priority") or "medium").lower()
        if priority not in VALID_PRIORITIES:
            priority = "medium"

        quest = unfinished.get(quest_id)
        recommended_action = _safe_text(advice.get("recommended_action"), 120)
        if quest and not recommended_action:
            recommended_action = f"Complete {quest.get('title')}"

        action_type = "quests"
        action_path = "/quests"
        action_label = "Start Quest"
        if quest_id:
            action_type = "quest"
            action_path = "/quests"
            action_label = "Start Quest"
        elif boss_id:
            action_type = "boss"
            action_path = f"/boss/{boss_id}"
            action_label = "Enter Boss"
        elif skill_id or (recommended_action and "skill" in recommended_action.lower()):
            action_type = "skills"
            action_path = "/skills"
            action_label = "View Skills"
        elif region:
            region_id = next((rid for rid, info in REGIONS.items() if info["name"] == region), None)
            action_type = "region"
            action_path = f"/world/{region_id}" if region_id else "/world"
            action_label = f"View {region}"

        return {
            "message": _safe_text(advice.get("message") or "Stay the course, Adventurer.", 500),
            "priority": priority,
            "recommended_action": recommended_action or "View your quests",
            "region": region,
            "quest_id": quest_id,
            "boss_id": boss_id,
            "skill_id": skill_id,
            "reason": _safe_text(advice.get("reason"), 300),
            "action_type": action_type,
            "action_path": action_path,
            "action_label": action_label,
        }

    def _call_provider(self, user_state: Dict[str, Any]) -> str:
        prompt = self._build_prompt(user_state)
        system = (
            "You are the Game Master for Life RPG. Use ONLY the provided game state. "
            "Never invent quest IDs, boss IDs, or skill IDs. Never mention passwords or personal data. "
            "Return JSON with keys: message, priority, recommended_action, region, quest_id, boss_id, skill_id, reason. "
            "priority must be high, medium, or low. quest_id/boss_id/skill_id must be integers from the data or null."
        )
        return self._http_chat(system, prompt)

    def _http_chat(self, system: str, prompt: str) -> str:
        if self.provider == "anthropic":
            body = {
                "model": self.model,
                "max_tokens": 350,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            }
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
        else:
            body = {
                "model": self.model,
                "temperature": 0.4,
                "max_tokens": 350,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            }
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError("AI network failure") from exc

        if self.provider == "anthropic":
            return payload["content"][0]["text"]
        return payload["choices"][0]["message"]["content"]

    def _build_prompt(self, user_state: Dict[str, Any]) -> str:
        signals = user_state.get("signals") or self.compute_signals(user_state)
        safe_quests = [
            {
                "id": q.get("id"),
                "title": q.get("title"),
                "category": q.get("category"),
                "difficulty": q.get("difficulty"),
                "xp_reward": q.get("xp_reward"),
            }
            for q in (user_state.get("unfinished_quests") or [])[:8]
        ]
        active_boss = user_state.get("active_boss")
        boss_safe = None
        if active_boss:
            boss_safe = {
                "id": active_boss.get("id"),
                "title": active_boss.get("title"),
                "hp_percent": active_boss.get("hp_percent"),
                "category": active_boss.get("category"),
                "phase": active_boss.get("phase"),
            }
        skill_safe = None
        rec = user_state.get("recommended_skill")
        if rec:
            skill_safe = {"id": rec.get("id"), "name": rec.get("name"), "attribute": rec.get("attribute")}

        payload = {
            "level": user_state.get("level"),
            "class": user_state.get("class"),
            "attributes": user_state.get("attributes"),
            "streak": user_state.get("streak"),
            "world_progress": user_state.get("world_progress"),
            "skill_points": user_state.get("skill_points"),
            "region_progress": user_state.get("region_progress"),
            "weakest_region": signals.get("weakest_region"),
            "strongest_region": signals.get("strongest_region"),
            "active_boss": boss_safe,
            "unfinished_quests": safe_quests,
            "recommended_skill": skill_safe,
            "life_goals": user_state.get("life_goals"),
        }
        return (
            "Recommend ONE action for today based on this game state JSON.\n"
            + json.dumps(payload)
            + "\nOnly use quest/boss/skill IDs listed above."
        )

    def _parse_ai_response(self, advice_text: str, user_state: Dict[str, Any]) -> Dict[str, Any]:
        data = json.loads(self._extract_json(advice_text))
        if not isinstance(data, dict):
            raise ValueError("AI did not return an object")
        return data

    @staticmethod
    def _extract_json(text: str) -> str:
        text = (text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object")
        return text[start : end + 1]

    @staticmethod
    def _store_cache(user_id: Optional[int], advice: Dict[str, Any]):
        if user_id is None:
            return
        _advice_cache[int(user_id)] = {"ts": time.time(), "advice": advice}

    @staticmethod
    def clear_cache(user_id: Optional[int] = None):
        if user_id is None:
            _advice_cache.clear()
        else:
            _advice_cache.pop(int(user_id), None)


game_master = GameMasterService()
