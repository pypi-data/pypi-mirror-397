# culturecoded

Official Python SDK for the CultureCoded Cultural UX Intelligence Platform.

Analyze designs for cultural adaptation and get AI-powered recommendations based on 11 cross-cultural research frameworks from researchers worldwide.

## Installation

```bash
pip install culturecoded
```

**Requirements:** Python 3.8+

## Getting Started

### 1. Create an Account

Sign up for a CultureCoded account at [culturecoded.io](https://culturecoded.io) to get access to the platform.

### 2. Get Your API Key

1. Log in to your [CultureCoded Dashboard](https://culturecoded.io)
2. Navigate to **Settings** > **API Keys**
3. Click **Generate New API Key**
4. Copy your API key (starts with `cc_live_`)

> **Important:** Keep your API key secure. Never commit it to version control or expose it in client-side code.

### 3. Set Up Your Environment

We recommend storing your API key as an environment variable:

```bash
# .env file (add to .gitignore!)
CULTURECODED_API_KEY=cc_live_your_api_key_here
```

For different environments:
- **Local development**: Use `python-dotenv` to load `.env` files
- **Django**: Add to `settings.py` or use `django-environ`
- **Flask**: Use `python-dotenv` or Flask's config
- **AWS Lambda/Cloud Functions**: Use environment variables in console

### 4. Initialize the SDK

```python
import os
from culturecoded import CultureCoded

cc = CultureCoded(api_key=os.environ["CULTURECODED_API_KEY"])
```

## Quick Start

```python
import os
from culturecoded import CultureCoded

cc = CultureCoded(api_key=os.environ["CULTURECODED_API_KEY"])

# Analyze a design for cultural adaptation
analysis = cc.analyze_design(
    image_url="https://example.com/landing-page.png",
    target_region="Africa",
    target_country="Nigeria",
    ethnic_group="Yoruba",  # Optional: target specific cultural community
    design_type="landing_page",
    industry="fintech"
)

# Get recommendations
for rec in analysis.recommendations:
    print(f"{rec.category} ({rec.priority}): {rec.suggestion}")
```

## Pricing & Credits

CultureCoded uses a credit-based system:

| Tier | Credits/Month | Price |
|------|---------------|-------|
| Starter | 50 | Free |
| Professional | 500 | $29/month |
| Enterprise | Unlimited | Custom |

Each design analysis costs credits based on complexity. Check your remaining credits:

```python
user = cc.get_user()
print(f"Credits remaining: {user.credits}")
```

## API Reference

### Initialization

```python
cc = CultureCoded(
    api_key="your-api-key",  # Required
    base_url="https://culturecoded.replit.app"  # Optional, defaults to production
)
```

### Cultural Analysis

#### `analyze_design()`

Analyze a design for cultural adaptation recommendations.

```python
analysis = cc.analyze_design(
    image_url="https://example.com/design.png",
    # or image_base64="base64-encoded-image-data",
    target_region="Africa",
    target_country="Nigeria",
    ethnic_group="Yoruba",  # Optional
    design_type="landing_page",
    industry="fintech"  # Optional
)
```

**Design Types:** `landing_page`, `mobile_app`, `dashboard`, `ecommerce`, `social_media`, `email`, `advertisement`, `other`

**Regions:** `Africa`, `Asia-Pacific`, `Europe`, `Latin America`, `Middle East`, `North America`

#### `get_analyses()`

Get all analyses for the authenticated user.

```python
analyses = cc.get_analyses()
```

#### `get_analysis(analysis_id)`

Get a specific analysis by ID.

```python
analysis = cc.get_analysis("analysis-id")
```

### Cultural Communities

#### `get_ethnic_groups(country)`

Get available cultural communities for more targeted analysis.

```python
groups = cc.get_ethnic_groups("Nigeria")
for group in groups:
    print(f"{group.name}: {group.cultural_dimensions}")
```

#### `get_regions()`

Get all available regions and countries.

```python
regions = cc.get_regions()
# {"Africa": ["Nigeria", "Kenya", ...], "Asia-Pacific": [...], ...}
```

### Export & Integrations

#### `export_analysis()`

Export an analysis in various formats.

```python
# Export to PDF
pdf_export = cc.export_analysis("analysis-id", format="pdf")
print(pdf_export.download_url)

# Export to Figma
figma_export = cc.export_analysis(
    "analysis-id",
    format="figma",
    figma_file_key="your-figma-file-key"
)
```

#### `export_to_figma(analysis_id, figma_file_key)`

Shorthand for Figma export.

```python
figma_export = cc.export_to_figma("analysis-id", "figma-file-key")
```

### User & Credits

#### `get_user()`

Get current user profile including credits and tier.

```python
user = cc.get_user()
print(f"Credits remaining: {user.credits}")
print(f"Tier: {user.tier}")
```

#### `get_usage()`

Get API usage statistics.

```python
usage = cc.get_usage()
print(f"Analyses this month: {usage.analyses_this_month}")
```

## Type Hints

This SDK includes full type hints for IDE support:

```python
from culturecoded import (
    CultureCoded,
    Analysis,
    Recommendation,
    EthnicGroup,
    CulturalDimensions,
)
```

## Error Handling

The SDK raises typed exceptions for different scenarios:

```python
from culturecoded import CultureCoded, CultureCodedError

cc = CultureCoded(api_key=os.environ["CULTURECODED_API_KEY"])

try:
    analysis = cc.analyze_design(...)
except CultureCodedError as e:
    if e.status_code == 401:
        print("Invalid API key")
    elif e.status_code == 402:
        print("Insufficient credits - upgrade your plan")
    elif e.status_code == 429:
        print("Rate limit exceeded - slow down requests")
    else:
        print(f"Error: {e.message}")
```

## Examples

### Batch Analysis

```python
import asyncio
from culturecoded import CultureCoded

cc = CultureCoded(api_key=os.environ["CULTURECODED_API_KEY"])

designs = [
    {"url": "https://example.com/landing.png", "type": "landing_page"},
    {"url": "https://example.com/checkout.png", "type": "ecommerce"},
]

analyses = []
for design in designs:
    analysis = cc.analyze_design(
        image_url=design["url"],
        design_type=design["type"],
        target_region="Africa",
        target_country="Nigeria"
    )
    analyses.append(analysis)
```

### Using with Django

```python
# views.py
import os
from django.http import JsonResponse
from culturecoded import CultureCoded

cc = CultureCoded(api_key=os.environ["CULTURECODED_API_KEY"])

def analyze_design_view(request):
    image_url = request.POST.get("image_url")
    target_country = request.POST.get("target_country")
    
    analysis = cc.analyze_design(
        image_url=image_url,
        target_region="Africa",
        target_country=target_country,
        design_type="landing_page"
    )
    
    return JsonResponse({
        "id": analysis.id,
        "recommendations": [
            {"category": r.category, "suggestion": r.suggestion}
            for r in analysis.recommendations
        ]
    })
```

### Using with Flask

```python
# app.py
import os
from flask import Flask, request, jsonify
from culturecoded import CultureCoded

app = Flask(__name__)
cc = CultureCoded(api_key=os.environ["CULTURECODED_API_KEY"])

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    
    analysis = cc.analyze_design(
        image_url=data["image_url"],
        target_region="Africa",
        target_country=data["target_country"],
        design_type="landing_page"
    )
    
    return jsonify({
        "id": analysis.id,
        "recommendations": [r.__dict__ for r in analysis.recommendations]
    })
```

## Research Frameworks

CultureCoded's AI analysis incorporates 11 cross-cultural HCI research frameworks:

### Western Foundational
- **Hofstede's Cultural Dimensions** (Netherlands)
- **Hall's Context Theory** (USA)
- **Trompenaars' 7 Dimensions** (Netherlands/UK)
- **Lewis Model** (UK)
- **Marcus User-Centered Design** (USA)

### East Asian HCI
- **Rau's Cross-Cultural Framework** (China)
- **Nisbett's Holistic-Analytic Cognition** (East-West)

### Global South HCI
- **Sun's Discursive Affordances** (China/USA)
- **Rajamanickam's Information Design** (India)
- **Bidwell's Afro-centric HCI** (South Africa)
- **Moalosi's Ubuntu Design Philosophy** (Botswana)

## Support

- **Documentation:** [culturecoded.io/api-docs](https://culturecoded.io/api-docs)
- **Dashboard:** [culturecoded.io](https://culturecoded.io)
- **Figma Plugin:** [Figma Community](https://www.figma.com/community/plugin/culturecoded)
- **Email:** support@culturecoded.io
- **GitHub Issues:** [Report bugs](https://github.com/culturecoded/sdk-python/issues)

## License

MIT
