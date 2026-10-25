---
name: codewars-agent
description: >-
  Use this skill whenever the user wants to analyze their Codewars profile, categorize completed katas into programming topics, or hunt for new unsolved katas based on topic, kyu level, and desired quantity, and save them into Google Sheets.
---

# Codewars Agent Skill

This skill guides the agent to perform two main tasks:
1. **Profile Analysis**: Read all completed katas for a Codewars username, analyze problem statements and tags, and categorize them into pure programming topics (`while_loop`, `for_loop`, `string`, `list`, `arithmetic_operators`, `if_related_homework`, `oop`, `regular_expressions`, `algorithms`, `dictionary`, `built_in`, `logics`).
2. **New Kata Hunting**: Search Codewars for katas matching a requested programming topic and kyu difficulty, verify they have never been solved by the user (0% duplicate), **strictly ensure they are solvable in Python**, perform deep relevance analysis on each kata, and save the results into Google Sheets with green table formatting (`#0D6133`).

## Architecture

```
User Request
    │
    ├──▶ Analyze Profile
    │       ├── GET /api/v1/users/{username}/code-challenges/completed
    │       ├── Topic Classification (TopicClassifier - Pure Programming Standards)
    │       └── Sync to Google Sheets (SheetsClient - 1-rasm & 2-rasm format)
    │
    └──▶ Hunt New Katas
            ├── Extract user's solved IDs (solved_ids)
            ├── Search candidate katas by topic & kyu (Python search)
            ├── Filter: Skip any kata where id in solved_ids
            ├── Strict Language Check: 'python' in kata_details['languages']
            ├── Deep Analysis: Implementation-based topic verification
            └── Save to Google Sheets (Green header formatting, Lanaguage='Python')
```

## Available Tools

The skill provides reusable tools in `tools/`:
- `codewars_client.py`: API client for completed katas, python search, and full kata details.
- `topic_classifier.py`: Classification and relevance analysis engine based on actual Python code implementation.
- `sheets_client.py`: Google Sheets client applying 2-rasm green header styling (`#0D6133`).

## Usage Examples

### 1. Profilni tahlil qilish:
```bash
/home/sanjar/Desktop/lessons/env/bin/python3 /home/sanjar/Desktop/lessons/codewars_agent.py analyze --user Sanjar_2002 --sheet 17_vwGPdOGXwsiukClGIV4snpjOw-vRu4Ob67VPY2GrM
```

### 2. Yangi (ishlanmagan) masalalarni qidirib topish (Faqat Python):
```bash
/home/sanjar/Desktop/lessons/env/bin/python3 /home/sanjar/Desktop/lessons/codewars_agent.py hunt --user Sanjar_2002 --topic "while_loop" --kyu "8 kyu" --count 5 --sheet 1VWc8OrNu-d-aj33zMq0hSBR7r5lf0jczVmQdHGnCZPs
```
