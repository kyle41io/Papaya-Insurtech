# AI Challenge 01 - Insurance Plan Comparison Page

Live URL: `https://kyle41io.github.io/Papaya-Insurtech/AI_Challenge_01/`

## Overview

This is a static HTML/CSS/JavaScript implementation of Papaya Insurtech's beginner AI Engineering Challenge 01. It renders the three required insurance plans side by side and highlights the strongest option in each comparison row.

## Timeline Estimate

- Requirement analysis and plan: 30 minutes
- UI design and static layout: 60 minutes
- Data rendering and comparison logic: 45 minutes
- Responsive QA and deployment: 30 minutes

Estimated total: 2.5 hours.

## Design Decisions

- The page uses Papaya's magenta brand color, clean white surfaces, and restrained dark navy text to create a professional insurance/fintech feel.
- Bronze, Silver, and Gold each have their own visual treatment so the tier differences are visible even before reading the numbers.
- The table is optimized for desktop review, while mobile switches to stacked plan comparisons so every field remains readable.

## Recommendation Logic

The recommended plan is calculated from:

- included benefit categories
- annual coverage limit
- copay percentage
- waiting period
- coverage efficiency relative to monthly premium
- a premium penalty so the highest-priced plan does not win by default

Using this model, Silver is recommended as the best value-for-money option because it adds dental coverage, lowers copay, shortens the waiting period, and meaningfully increases coverage while remaining much more affordable than Gold.

## Local Run

Open `index.html` directly in a browser, or run a local static server:

```bash
python3 -m http.server 8080
```

Then visit:

```text
http://localhost:8080/AI_Challenge_01/
```
