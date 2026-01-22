# Gamification Feature - README

## Overview

The gamification feature is designed to motivate and engage patients in their health journey by rewarding them for consistent symptom tracking, maintaining healthy habits, and achieving milestones. The system includes badges, points, levels, streaks, challenges, and rewards.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Database Setup](#database-setup)
3. [How to Earn Achievements](#how-to-earn-achievements)
4. [System Components](#system-components)
5. [API Endpoints](#api-endpoints)
6. [Admin Interface](#admin-interface)

---

## How It Works

### Core Mechanics

1. **Points System**: Patients earn points for various activities (e.g., logging symptoms = 10 points)
2. **Level System**: Levels are calculated from total points using the formula: `level = sqrt(points / 100) + 1`
3. **Badge System**: Badges are automatically awarded when patients meet specific criteria
4. **Streak System**: Tracks consecutive days of activity (e.g., daily symptom logging)
5. **Challenges**: Time-limited goals that patients can join and complete
6. **Rewards**: Points-based rewards that patients can claim

### Automatic Triggers

The system automatically:
- Awards points when patients log symptoms
- Checks for badge eligibility after each activity
- Updates streaks for daily activities
- Calculates level ups when points thresholds are reached
- Creates activity feed entries for social features

---

## Database Setup

### 1. Initial Badge Seeding

Before patients can earn badges, you need to seed the initial badges into the database:

```bash
python manage.py seed_badges
```

This command creates the following default badges:

#### Symptom Tracking Badges
- **First Steps** (Common, 50 pts): Log your first symptom entry
- **Dedicated Logger** (Uncommon, 150 pts): Log symptoms 10 times
- **Wellness Warrior** (Rare, 300 pts): Log symptoms 30 times

#### Consistency Badges
- **Week Warrior** (Uncommon, 100 pts): Log symptoms for 7 consecutive days
- **Monthly Champion** (Rare, 500 pts): Log symptoms for 30 consecutive days
- **Daily Dedication** (Uncommon, 150 pts): Log symptoms for 7 days in a week

#### Milestone Badges
- **Century Club** (Common, 0 pts): Earn 100 points
- **Point Master** (Uncommon, 0 pts): Earn 500 points
- **Rising Star** (Rare, 0 pts): Reach Level 5
- **Badge Collector** (Uncommon, 200 pts): Earn 5 badges

### 2. Creating Custom Badges (via Django Admin)

You can create additional badges through the Django Admin interface:

1. Navigate to **Patient Portal > Badges**
2. Click **Add Badge**
3. Fill in the required fields:
   - **Name**: Badge name (e.g., "100 Day Streak")
   - **Description**: What the badge represents
   - **Category**: Choose from:
     - `symptom_tracking`
     - `consistency`
     - `wellness`
     - `milestone`
     - `social`
     - `treatment`
   - **Rarity**: Choose from:
     - `common`
     - `uncommon`
     - `rare`
     - `epic`
     - `legendary`
   - **Points Reward**: Points awarded when badge is earned
   - **Criteria** (JSON format): Define how to earn the badge

#### Badge Criteria Examples

**Symptom Logging Badge:**
```json
{
    "action": "log_symptoms",
    "count": 50,
    "period": "all_time"
}
```

**Streak Badge:**
```json
{
    "action": "maintain_streak",
    "days": 14,
    "period": "current"
}
```

**Points Badge:**
```json
{
    "action": "earn_points",
    "count": 1000,
    "period": "total"
}
```

**Level Badge:**
```json
{
    "action": "reach_level",
    "count": 10
}
```

**Weekly Activity Badge:**
```json
{
    "action": "log_symptoms",
    "count": 7,
    "period": "days",
    "days": 7
}
```

### 3. Creating Health Challenges

1. Navigate to **Patient Portal > Health Challenges**
2. Click **Add Health Challenge**
3. Configure:
   - **Title**: Challenge name
   - **Description**: What patients need to do
   - **Challenge Type**: symptom_logging, wellness, consistency, etc.
   - **Goal Description**: Clear goal statement
   - **Goal Value**: Numeric target (e.g., 7 for 7 days)
   - **Goal Unit**: "days", "times", etc.
   - **Start/End Date**: Challenge duration
   - **Points Reward**: Points for completion
   - **Badge Reward** (optional): Badge awarded on completion
   - **Status**: Set to "active" to make it available

### 4. Creating Rewards

1. Navigate to **Patient Portal > Rewards**
2. Click **Add Reward**
3. Configure:
   - **Name**: Reward name
   - **Description**: What the reward is
   - **Reward Type**: points, badge, discount, virtual, custom
   - **Points Required**: Points needed to claim
   - **Level Required**: Minimum level needed
   - **Max Claims**: Total available (null = unlimited)
   - **Max Claims Per User**: How many times a user can claim

---

## How to Earn Achievements

### Earning Points

Patients earn points automatically for:

| Activity | Points | When |
|----------|--------|------|
| Log Symptoms | 10 | Every time a symptom log is submitted |
| Earn Badge | Varies | When a badge is earned (badge-specific) |
| Complete Challenge | Varies | When a challenge is completed (challenge-specific) |

### Earning Badges

Badges are **automatically awarded** when patients meet the criteria. Here's how to earn each default badge:

#### 🏆 First Steps
- **How**: Log your first symptom entry
- **Points**: 50
- **Rarity**: Common

#### 📅 Week Warrior
- **How**: Log symptoms for 7 consecutive days (maintain a 7-day streak)
- **Points**: 100
- **Rarity**: Uncommon
- **Tip**: Log symptoms every day without missing a day

#### 🏅 Monthly Champion
- **How**: Log symptoms for 30 consecutive days (maintain a 30-day streak)
- **Points**: 500
- **Rarity**: Rare
- **Tip**: Consistency is key! Don't miss a single day.

#### 📋 Dedicated Logger
- **How**: Log symptoms 10 times total (doesn't need to be consecutive)
- **Points**: 150
- **Rarity**: Uncommon
- **Tip**: Keep logging regularly, even if you miss some days

#### ⭐ Century Club
- **How**: Earn 100 total points
- **Points**: 0 (milestone badge)
- **Rarity**: Common
- **Tip**: Log symptoms regularly to accumulate points

#### 🎖️ Point Master
- **How**: Earn 500 total points
- **Points**: 0 (milestone badge)
- **Rarity**: Uncommon
- **Tip**: Stay consistent with logging and earn badges

#### ⭐ Rising Star
- **How**: Reach Level 5
- **Points**: 0 (milestone badge)
- **Rarity**: Rare
- **Tip**: Level 5 requires approximately 1,600 points

#### 🏆 Badge Collector
- **How**: Earn 5 different badges
- **Points**: 200
- **Rarity**: Uncommon
- **Tip**: Focus on different badge categories

#### 📆 Daily Dedication
- **How**: Log symptoms for 7 days within a 7-day period
- **Points**: 150
- **Rarity**: Uncommon
- **Tip**: Log every day for a week

#### ❤️ Wellness Warrior
- **How**: Log symptoms 30 times total (doesn't need to be consecutive)
- **Points**: 300
- **Rarity**: Rare
- **Tip**: Long-term commitment pays off

### Leveling Up

Levels are calculated automatically based on total points:

- **Level 1**: 0-99 points
- **Level 2**: 100-399 points
- **Level 3**: 400-899 points
- **Level 4**: 900-1,599 points
- **Level 5**: 1,600-2,499 points
- **Level 10**: 9,000-10,899 points
- And so on...

**Formula**: `level = sqrt(points / 100) + 1`

### Maintaining Streaks

- **Current Streak**: Consecutive days of activity (resets if you miss a day)
- **Longest Streak**: Your best streak ever (never decreases)
- **How to maintain**: Log symptoms every day without gaps

### Completing Challenges

1. View available challenges in the patient portal
2. Join a challenge (if it's active and you meet level requirements)
3. Complete the challenge goal (e.g., log symptoms for 7 days)
4. Automatically receive points and badge (if applicable)

### Claiming Rewards

1. Earn enough points and reach required level
2. Browse available rewards in the rewards section
3. Click "Claim Reward"
4. Points are deducted, reward is added to your account

---

## System Components

### Models

#### Badge
- Stores badge definitions and criteria
- Categories: symptom_tracking, consistency, wellness, milestone, social, treatment
- Rarity levels: common, uncommon, rare, epic, legendary

#### UserBadge
- Tracks which badges each user has earned
- One badge per user (unique constraint)
- Stores when badge was earned

#### UserProgress
- Tracks user's overall progress
- Fields:
  - `total_points`: Current points (can decrease if spent)
  - `lifetime_points`: Total points ever earned (never decreases)
  - `level`: Current level
  - `current_streak`: Consecutive days
  - `longest_streak`: Best streak ever
  - `total_symptom_logs`: Count of logs
  - `total_badges_earned`: Count of badges
  - `weekly_points`: Points earned this week
  - `monthly_points`: Points earned this month

#### HealthChallenge
- Time-limited challenges
- Can have goals, rewards, and participation limits

#### ChallengeParticipation
- Tracks user participation in challenges
- Monitors progress toward challenge goals

#### Reward
- Rewards that can be claimed with points
- Can be points, badges, discounts, or custom rewards

#### UserReward
- Tracks rewards claimed by users

#### ActivityFeed
- Social activity feed showing user achievements
- Can be public, friends-only, or private

#### LeaderboardEntry
- Rankings for daily, weekly, monthly, and all-time periods

### Services

#### GamificationService
Main service class with static methods:

- `check_and_award_badges()`: Checks and awards badges based on activity
- `award_points()`: Awards points for activities
- `check_level_up()`: Checks if user leveled up
- `get_user_stats()`: Returns comprehensive user statistics
- `get_or_create_progress()`: Gets or creates UserProgress for a user

### Signals

The system uses Django signals to automatically trigger gamification:

- **post_save on PatientSymptomLog**: 
  - Awards 10 points
  - Checks for badge eligibility
  - Updates streak
  - Checks for level up

---

## API Endpoints

### Get User Stats
```
GET /api/user-stats/
```
Returns: level, total_points, current_streak, longest_streak, total_badges, etc.

### Check New Badges
```
GET /api/check-new-badges/
```
Returns: newly earned badges and level up information

### Get Unread Alerts Count
```
GET /api/unread-alerts-count/
```
Returns: count of unread alerts

### Get Symptom Trend
```
GET /api/symptom-trend/?days=14
```
Returns: symptom trend data for charts

---

## Admin Interface

All gamification models are registered in Django Admin:

1. **Badges**: Create, edit, and manage badges
2. **User Badges**: View which users have earned which badges
3. **User Progress**: View user statistics and progress
4. **Health Challenges**: Create and manage challenges
5. **Challenge Participations**: View challenge participation
6. **Rewards**: Create and manage rewards
7. **User Rewards**: View claimed rewards
8. **Friend Requests**: Manage friend requests (social features)
9. **Leaderboard Entries**: View leaderboard rankings
10. **Activity Feed**: View activity feed entries

---

## Quick Start Guide

### For Administrators

1. **Seed Initial Badges**:
   ```bash
   python manage.py seed_badges
   ```

2. **Create Challenges** (optional):
   - Go to Django Admin
   - Navigate to Health Challenges
   - Create challenges with goals and rewards

3. **Create Rewards** (optional):
   - Go to Django Admin
   - Navigate to Rewards
   - Create rewards with point requirements

### For Patients

1. **Start Logging Symptoms**:
   - Log symptoms daily to earn points
   - Each log = 10 points

2. **Maintain Streaks**:
   - Log every day without gaps
   - Earn streak badges (7 days, 30 days)

3. **Earn Badges**:
   - Badges are automatically awarded
   - Check your profile to see earned badges

4. **Level Up**:
   - Earn points to level up
   - Higher levels unlock more rewards

5. **Join Challenges**:
   - Browse available challenges
   - Complete goals to earn rewards

6. **Claim Rewards**:
   - Save up points
   - Claim rewards from the rewards section

---

## Tips for Maximum Engagement

1. **Daily Logging**: Log symptoms every day to maintain streaks and earn consistency badges
2. **Variety**: Try to earn badges from different categories
3. **Challenges**: Join active challenges for bonus points
4. **Long-term**: Focus on long-term goals (30-day streaks, high point totals)
5. **Social**: Connect with friends to see their achievements (if social features are enabled)

---

## Technical Notes

- **Level Calculation**: Uses square root formula for exponential growth
- **Streak Logic**: Resets if a day is missed (no grace period)
- **Badge Uniqueness**: Each badge can only be earned once per user
- **Points Reset**: Weekly and monthly points reset automatically
- **Automatic Processing**: All gamification happens automatically via signals
- **Activity Feed**: All achievements are logged in the activity feed

---

## Support

For questions or issues with the gamification system:
1. Check Django Admin for badge/challenge/reward configurations
2. Verify UserProgress exists for the user
3. Check signals are properly connected
4. Review activity logs in ActivityFeed model

---

**Last Updated**: Based on current codebase structure
**Version**: 1.0

