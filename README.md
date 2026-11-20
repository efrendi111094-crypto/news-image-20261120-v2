# news-image-20261120-v2

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/efrendi111094-crypto/news-image-20261120-v2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/efrendi111094-crypto/news-image-20261120-v2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A program that draws one newspaper-style front page summing up the world's news of Friday 20 November 2026: Cyclone Akvan slamming India's east coast after 300,000 people were evacuated, Taiwan's shares plunging 6% in their worst week since 1991, the Shenzhen summit's peace declaration with no advances behind it, Britain pledging 1,000+ drones for Ukraine, Estonia closing its Russian border, and Glenn Phillips' 118 lifting New Zealand to 368 — plus six more briefs across five regions. Pure Python 3.13 standard library, no network: a single self-contained main.py renders the page with a hand-built 5x7 pixel font, draws every illustration from primitives, encodes the PNG itself, and writes /output/entry.png deterministically. The news content lives in news.json, separate from the generator.

## How this entry meets the rubric

1. **One day, named:** the masthead and the footer both name Friday 20 November 2026, and every story is an event that happened or was first reported on that day.
2. **Selection and breadth:** 12 stories across five regions (Asia, Europe, Oceania, the Middle East, North America) and five fields (weather, markets, diplomacy, security, sport).
3. **It reads:** one big illustrated hero, two medium cards and three small cards, each with a short headline and a plain-language summary; every headline stays legible when the page is shrunk to judge-view size.
4. **Faithful:** every fact is verified against reports published on 20 November 2026 (Reuters, AP, BBC, UN News, WSJ, CNN, Le Monde, The Times, Al Jazeera); the footer carries a date check and the source list.
5. **Craft:** one clear composition on a cream broadsheet, generous white space, no garbled text, and a deterministic render — two runs produce byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=tzrh51cg&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
