<p align="center">
  <img src="https://discourses.io/logo.svg" alt="Discourses" width="280" />
</p>

<h1 align="center">Discourses Python SDK</h1>

<p align="center">
  <strong>Institutional-grade financial sentiment analysis with era-calibrated lexicons</strong>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/discourses"><img src="https://badge.fury.io/py/discourses.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="https://discourses.io/research"><strong>📄 Read the Whitepaper</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="https://discourses.io/documentation/methodology"><strong>🔬 Methodology</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="https://discourses.io/documentation"><strong>📖 Documentation</strong></a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="https://discourses.io/dashboard"><strong>🔑 Get API Key</strong></a>
</p>

---

## Why Discourses?

Traditional sentiment analysis treats language as static. But financial language evolves—"disruption" meant crisis in 2008, innovation by 2020. **Discourses** solves this with **era-calibrated lexicons** built on peer-reviewed academic research.

| Era | Period | What Changed |
|:---:|:------:|:-------------|
| **ERA_1** | 2007–2011 | Crisis vocabulary, early social trading |
| **ERA_2** | 2012–2015 | QE-era optimism, regulatory terminology |
| **ERA_3** | 2016–2019 | Algorithmic trading, crypto emergence |
| **ERA_4** | 2020–now | Pandemic markets, retail revolution, meme stocks |

---

## Installation

```bash
pip install discourses
```

---

## Quick Start

```python
from discourses import Discourses

client = Discourses(api_key="your-api-key")
result = client.analyze("Apple reported record quarterly earnings")

print(result.sentiment)  # "positive"
print(result.score)      # 0.72
```

---

## API Reference

### 🔑 Initialize the Client

Every request requires authentication with your API key. Get yours at [discourses.io/dashboard](https://discourses.io/dashboard).

```python
from discourses import Discourses

client = Discourses(api_key="your-api-key")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | *required* | Your Discourses API key |
| `base_url` | `str` | `https://discourses.io/api/v1` | API base URL |
| `timeout` | `int` | `30` | Request timeout in seconds |

---

## Endpoints

<br>

### 📊 Analyze — Single Text Sentiment

> **`POST /analyze`** — [Documentation](https://discourses.io/documentation#analyze)

Analyze sentiment of any financial text using an era-specific lexicon. Returns a score from -1.0 (bearish) to +1.0 (bullish) with confidence metrics.

```python
from discourses import Discourses, Era

# Initialize client
client = Discourses(api_key="your-api-key")

# Analyze text with modern lexicon (default)
result = client.analyze(
    text="Tesla exceeds delivery expectations, stock surges in after-hours trading",
    era=Era.ERA_4
)

# Access the results
print(f"Score:      {result.score}")
print(f"Sentiment:  {result.sentiment}")
print(f"Magnitude:  {result.magnitude}")
print(f"Confidence: {result.confidence}")
print(f"Words:      {result.word_count}")
```

**Expected Output:**

```
Score:      0.78
Sentiment:  positive
Magnitude:  0.82
Confidence: 0.94
Words:      11
```

<details>
<summary><strong>Response Object: <code>AnalysisResult</code></strong></summary>

| Field | Type | Description |
|-------|------|-------------|
| `score` | `float` | Sentiment score from -1.0 to +1.0 |
| `sentiment` | `str` | `"positive"`, `"negative"`, or `"neutral"` |
| `magnitude` | `float` | Strength of sentiment (0.0 to 1.0) |
| `confidence` | `float` | Model confidence (0.0 to 1.0) |
| `era` | `str` | Era lexicon used |
| `word_count` | `int` | Number of words analyzed |
| `matches` | `list` | Sentiment words found with scores |

**Helper Properties:**
- `result.is_positive` → `True` if sentiment is positive
- `result.is_negative` → `True` if sentiment is negative  
- `result.is_neutral` → `True` if sentiment is neutral

</details>

---

<br>

### 🔄 Compare — Cross-Era Analysis

> **`POST /compare`** — [Documentation](https://discourses.io/documentation#compare)

Analyze how the same text would be interpreted across different market eras. Essential for backtesting, historical analysis, and understanding semantic drift.

```python
from discourses import Discourses

# Initialize client
client = Discourses(api_key="your-api-key")

# Compare sentiment across all eras
comparison = client.compare(
    text="Aggressive disruption strategy threatens incumbent market leaders"
)

# View per-era sentiment
print("Era-by-Era Sentiment:")
print("-" * 40)
for era_result in comparison.results:
    bar = "█" * int(abs(era_result.score) * 20)
    sign = "+" if era_result.score >= 0 else "-"
    print(f"  {era_result.era}: {sign}{era_result.score:5.2f}  {bar}")

# Check semantic drift
print()
print(f"Semantic Drift: {comparison.drift.max_drift:.2f}")
print(f"Trend:          {comparison.drift.trend}")
```

**Expected Output:**

```
Era-by-Era Sentiment:
----------------------------------------
  era_1: -0.45  █████████
  era_2: -0.22  ████
  era_3: +0.18  ███
  era_4: +0.61  ████████████

Semantic Drift: 1.06
Trend:          increasing
```

> 💡 **Notice how "disruption" shifted from negative (crisis-era) to positive (innovation-era) across time periods.**

<details>
<summary><strong>Response Object: <code>CompareResult</code></strong></summary>

| Field | Type | Description |
|-------|------|-------------|
| `text` | `str` | Original analyzed text |
| `results` | `List[EraResult]` | Sentiment for each era |
| `drift` | `DriftAnalysis` | Drift metrics across eras |

**DriftAnalysis Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `max_drift` | `float` | Maximum score difference between any two eras |
| `min_score` | `float` | Lowest score across eras |
| `max_score` | `float` | Highest score across eras |
| `mean_score` | `float` | Average score |
| `trend` | `str` | `"increasing"`, `"decreasing"`, or `"stable"` |

**Helper Properties:**
- `comparison.drift.has_significant_drift` → `True` if drift exceeds 0.2

</details>

---

<br>

### ⚡ Batch — High-Volume Processing

> **`POST /batch`** — [Documentation](https://discourses.io/documentation#batch)

Efficiently analyze up to 100 texts in a single request. Supports both single-era analysis and cross-era comparison mode.

```python
from discourses import Discourses, Era

# Initialize client
client = Discourses(api_key="your-api-key")

# Headlines to analyze
headlines = [
    "Fed signals potential rate cuts amid cooling inflation",
    "Tech layoffs accelerate as recession fears mount",
    "Nvidia beats estimates on unprecedented AI chip demand",
    "Regional bank failures spark contagion concerns",
    "Consumer spending resilient despite economic headwinds",
]

# Batch analyze with ERA_4 lexicon
batch = client.batch(texts=headlines, era=Era.ERA_4)

# Process results
print("Headline Sentiment Analysis")
print("=" * 60)
for item in batch:
    emoji = "🟢" if item.result.is_positive else "🔴" if item.result.is_negative else "⚪"
    print(f"{emoji} [{item.result.score:+.2f}] {item.text[:50]}...")

print()
print(f"Processed: {batch.success_count}/{batch.total_count}")
print(f"Bullish:   {sum(1 for i in batch if i.result.is_positive)}")
print(f"Bearish:   {sum(1 for i in batch if i.result.is_negative)}")
```

**Expected Output:**

```
Headline Sentiment Analysis
============================================================
🟢 [+0.52] Fed signals potential rate cuts amid cooling inf...
🔴 [-0.68] Tech layoffs accelerate as recession fears mount...
🟢 [+0.84] Nvidia beats estimates on unprecedented AI chip ...
🔴 [-0.73] Regional bank failures spark contagion concerns...
🟢 [+0.31] Consumer spending resilient despite economic hea...

Processed: 5/5
Bullish:   3
Bearish:   2
```

#### Batch with Cross-Era Comparison

```python
# Enable cross-era comparison for each text
batch = client.batch(
    texts=headlines,
    compare_eras=True  # Analyze each text across all eras
)

# Access drift for each headline
for item in batch:
    drift = item.comparison.drift
    print(f"'{item.text[:40]}...'")
    print(f"  → Drift: {drift.max_drift:.2f} ({drift.trend})")
```

<details>
<summary><strong>Response Object: <code>BatchResult</code></strong></summary>

| Field | Type | Description |
|-------|------|-------------|
| `items` | `List[BatchItem]` | Results for each text |
| `total_count` | `int` | Total texts submitted |
| `success_count` | `int` | Successfully processed |
| `error_count` | `int` | Failed to process |

**BatchItem Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `index` | `int` | Position in original list |
| `text` | `str` | The analyzed text |
| `result` | `AnalysisResult` | Single-era result (if `compare_eras=False`) |
| `comparison` | `CompareResult` | Multi-era result (if `compare_eras=True`) |
| `error` | `str` | Error message if failed |

**Helper Methods:**
- `batch.get_successful()` → List of successful items
- `batch.get_failed()` → List of failed items
- `batch.all_succeeded` → `True` if no errors
- `len(batch)` → Number of items
- `batch[0]` → Access by index
- `for item in batch` → Iterate over items

</details>

---

## Error Handling

The SDK provides typed exceptions for robust error handling:

```python
from discourses import (
    Discourses,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    DiscoursesError,
)

client = Discourses(api_key="your-api-key")

try:
    result = client.analyze("Market analysis text")
    
except AuthenticationError:
    # Invalid or expired API key
    print("Check your API key at https://discourses.io/dashboard")
    
except RateLimitError as e:
    # Too many requests
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    
except ValidationError as e:
    # Invalid input (empty text, too long, etc.)
    print(f"Invalid input: {e.message}")
    
except DiscoursesError as e:
    # Catch-all for other API errors
    print(f"API error: {e}")
```

---

## Era Selection Guide

| Use Case | Recommended Era |
|----------|-----------------|
| Real-time market sentiment | `Era.ERA_4` |
| Backtesting 2020+ strategies | `Era.ERA_4` |
| Backtesting 2016–2019 | `Era.ERA_3` |
| Historical crisis analysis | `Era.ERA_1` |
| Understanding semantic drift | `client.compare()` |

```python
from discourses import Era

# Modern analysis (default)
client.analyze(text, era=Era.ERA_4)

# Historical analysis
client.analyze(text, era=Era.ERA_1)

# String values also work
client.analyze(text, era="era_2")
```

---

## Links

<table>
  <tr>
    <td align="center">📄</td>
    <td><a href="https://discourses.io/research"><strong>Whitepaper</strong></a><br>Academic research & methodology</td>
    <td align="center">📖</td>
    <td><a href="https://discourses.io/documentation"><strong>Documentation</strong></a><br>Full API reference</td>
  </tr>
  <tr>
    <td align="center">🔬</td>
    <td><a href="https://discourses.io/documentation/methodology"><strong>Methodology</strong></a><br>How era-calibration works</td>
    <td align="center">🔑</td>
    <td><a href="https://discourses.io/dashboard"><strong>Dashboard</strong></a><br>Get your API key</td>
  </tr>
  <tr>
    <td align="center">💬</td>
    <td><a href="https://github.com/discourses/discourses-python/issues"><strong>Issues</strong></a><br>Report bugs & requests</td>
    <td align="center">📦</td>
    <td><a href="https://pypi.org/project/discourses/"><strong>PyPI</strong></a><br>Package & versions</td>
  </tr>
</table>

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://discourses.io">Discourses</a></sub>
</p>
