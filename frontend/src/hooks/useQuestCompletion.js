import { useState } from "react";
import { useApp } from "../context/AppContext.jsx";
import { useToast } from "../context/ToastContext.jsx";
import * as api from "../api/api";

export function useQuestCompletion(onReload) {
  const { user, setUser } = useApp();
  const { addToast } = useToast();
  const [levelUp, setLevelUp] = useState(null);
  const [rewardPopup, setRewardPopup] = useState(null);
  const [bossDamage, setBossDamage] = useState(null);

  const handleComplete = async (id) => {
    try {
      const result = await api.completeQuest(id);
      if (result?.user) setUser(result.user);

      const events = result?.events || {};
      const levelsGained = events.levelsGained || 0;

      // Show reward popup first
      setRewardPopup({
        quest: result.quest,
        attributeGains: events.attributeGains,
        bossDamage: events.bossDamage,
      });

      // Then show level-up if applicable
      if (levelsGained > 0 && user?.settings?.levelUpCelebrations !== false) {
        setTimeout(() => {
          setLevelUp({
            level: events.newLevel,
            oldLevel: events.oldLevel,
            skillPoints: levelsGained,
            goldBonus: levelsGained * 100,
            characterClass: result.user?.class,
            evolution: events.evolution,
          });
        }, 1500); // Show level-up after reward popup
      }

      // Show boss damage animation if applicable
      const bossDmg = events.bossDamage;
      if (bossDmg && (typeof bossDmg === "number" ? bossDmg > 0 : bossDmg.damage > 0)) {
        const damageVal = typeof bossDmg === "number" ? bossDmg : bossDmg.damage;
        setBossDamage({
          damage: damageVal,
          isCritical: events.bossIsCritical || false,
          bossTitle: bossDmg.bossTitle,
          defeated: bossDmg.defeated,
        });
        setTimeout(() => setBossDamage(null), 2500);
      }

      if (events.dailyGoalCompleted && events.dailyGoalBonus) {
        addToast(
          `Daily goal complete! +${events.dailyGoalBonus.xp} XP, +${events.dailyGoalBonus.gold} Gold`,
          "success",
          5000
        );
      }

      if (events.achievementsUnlocked?.length && user?.settings?.achievementUnlocks !== false) {
        events.achievementsUnlocked.forEach((a) => {
          addToast(`Achievement unlocked: ${a.title}!`, "info", 5000);
        });
      }

      if (onReload) await onReload();
      return result;
    } catch (err) {
      addToast(api.getErrorMessage(err, "Failed to complete quest"), "error");
      throw err;
    }
  };

  const dismissLevelUp = () => setLevelUp(null);
  const dismissRewardPopup = () => setRewardPopup(null);
  const dismissBossDamage = () => setBossDamage(null);

  return { handleComplete, levelUp, dismissLevelUp, rewardPopup, dismissRewardPopup, bossDamage, dismissBossDamage };
}
