-- Life RPG database schema (MySQL 8+)
CREATE DATABASE IF NOT EXISTS life_rpg CHARACTER SET utf8mb4;
USE life_rpg;

CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(120) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(80)  NOT NULL,
    title           VARCHAR(80)  DEFAULT 'Adventurer',
    avatar          VARCHAR(10)  DEFAULT '🧙',
    level           INT DEFAULT 1,
    xp              INT DEFAULT 0,
    xp_to_next      INT DEFAULT 500,
    gold            INT DEFAULT 0,
    streak          INT DEFAULT 0,
    best_streak     INT DEFAULT 0,
    skill_points    INT DEFAULT 0,
    last_active_date DATE NULL,
    daily_goal      INT DEFAULT 5,
    daily_goal_bonus_date DATE NULL,
    quest_reminders     BOOLEAN DEFAULT TRUE,
    streak_alerts        BOOLEAN DEFAULT TRUE,
    levelup_celebrations  BOOLEAN DEFAULT TRUE,
    achievement_unlocks   BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attributes (
    user_id      INT PRIMARY KEY,
    strength     INT DEFAULT 0,
    intelligence INT DEFAULT 0,
    discipline   INT DEFAULT 0,
    creativity   INT DEFAULT 0,
    vitality     INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE quests (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    title         VARCHAR(150) NOT NULL,
    category      VARCHAR(30) NOT NULL,      -- Learning, Health, Creative, Work, Wellness
    difficulty    ENUM('EASY','MEDIUM','HARD') NOT NULL DEFAULT 'EASY',
    attribute     VARCHAR(30) NOT NULL,      -- which attribute it boosts
    xp_reward     INT NOT NULL DEFAULT 50,
    gold_reward   INT NOT NULL DEFAULT 10,
    due_label     VARCHAR(30) DEFAULT 'Today', -- Today, Tomorrow, This Week
    status        ENUM('ACTIVE','COMPLETED') DEFAULT 'ACTIVE',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at  TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE achievements (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    code         VARCHAR(50) NOT NULL UNIQUE,
    title        VARCHAR(80) NOT NULL,
    description  VARCHAR(200) NOT NULL,
    xp_reward    INT NOT NULL DEFAULT 100,
    icon         VARCHAR(10) DEFAULT '🏆'
);

CREATE TABLE user_achievements (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    achievement_id INT NOT NULL,
    unlocked_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_user_achievement (user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
);

CREATE TABLE shop_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(80) NOT NULL,
    category     VARCHAR(30) NOT NULL,   -- Avatars, Frames, Themes, Badges, Companions, Effects, Weapons, Magic
    description  VARCHAR(200),
    price        INT NOT NULL,
    icon         VARCHAR(10) DEFAULT '✨'
);

CREATE TABLE user_inventory (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    item_id     INT NOT NULL,
    equipped    BOOLEAN DEFAULT FALSE,
    owned_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_user_item (user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES shop_items(id) ON DELETE CASCADE
);

CREATE TABLE xp_log (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id   INT NOT NULL,
    log_date  DATE NOT NULL,
    xp_earned INT DEFAULT 0,
    quests_done INT DEFAULT 0,
    gold_earned INT DEFAULT 0,
    UNIQUE KEY uniq_user_date (user_id, log_date),
    INDEX idx_xp_log_user_date (user_id, log_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_inventory_user ON user_inventory (user_id);
CREATE INDEX idx_quests_user_id ON quests (user_id);
CREATE INDEX idx_quests_user_status ON quests (user_id, status);
