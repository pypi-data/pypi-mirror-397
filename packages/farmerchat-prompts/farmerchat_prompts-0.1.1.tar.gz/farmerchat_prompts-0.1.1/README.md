# FarmerChat Prompts

A Python library for managing AI prompts across multiple providers (OpenAI, Google Gemma, Llama) with domain-specific templates optimized for agricultural applications and prompt evaluation.

## Features

- 🤖 **Multi-Provider Support**: OpenAI GPT, Google Gemma, Meta Llama
- 🌾 **Multi-Domain Architecture**: Organized by use case domains
  - **Crop Advisory**: Agricultural guidance and farming practices
  - **Prompt Evaluation**: Fact extraction, validation, and quality assessment
- 🎯 **Optimized Prompts**: Each prompt follows provider-specific best practices
- 🔧 **Easy Integration**: Simple API to access prompts by provider, use case, and domain
- 📦 **Type Safe**: Built with Pydantic for runtime validation
- 🔄 **Backward Compatible**: Existing code works without changes

## Installation

```bash
pip install farmerchat-prompts
```

Or install from GitHub:

```bash
pip install git+https://github.com/digitalgreenorg/farmerchat-prompts.git
```

## Quick Start

### Basic Usage

```python
from farmerchat_prompts import PromptManager

# Initialize the prompt manager
manager = PromptManager()

# Get a crop advisory prompt (defaults to crop_advisory domain)
prompt = manager.get_prompt("openai", "crop_recommendation")

# Use with your AI client
from openai import OpenAI
client = OpenAI(api_key="your-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": prompt.system_prompt},
        {"role": "user", "content": "I have sandy soil in Bihar, what should I grow?"}
    ]
)
```

### Using Multiple Domains

```python
# Crop advisory prompts
crop_prompt = manager.get_prompt(
    provider="openai",
    use_case="crop_recommendation",
    domain="crop_advisory"
)

# Prompt evaluation prompts
eval_prompt = manager.get_prompt(
    provider="openai",
    use_case="specificity_evaluation",
    domain="prompt_evals"
)
```

## Supported Providers

- **OpenAI** (`openai`): GPT-3.5, GPT-4, GPT-4o, GPT-4o mini
- **Meta** (`llama`): Llama 3.1, Llama 3.2
- **Gemma** (`gemma`): Gemma-3n-E4B-it, Gemma 2, Gemma 7B/2B (Instruction Tuned)

## Domains & Use Cases

### 1. Crop Advisory Domain (`crop_advisory`)

Agricultural guidance for Indian farming contexts:

1. **crop_recommendation**: Crop suggestions based on soil, climate, and location
2. **pest_management**: Pest identification and treatment recommendations
3. **soil_analysis**: Soil test interpretation and improvement suggestions
4. **weather_advisory**: Weather-based farming guidance
5. **market_insights**: Market prices and selling recommendations

### 2. Prompt Evaluation Domain (`prompt_evals`)

**Why These Prompts Matter:**

When building AI-powered agricultural chatbots, ensuring response quality is critical. Farmers depend on accurate, specific, and actionable information. The prompt evaluation domain provides a comprehensive framework to:

- **Validate Response Quality**: Automatically assess if AI-generated advice is specific and actionable
- **Extract Structured Knowledge**: Convert conversational responses into verifiable atomic facts
- **Ensure Consistency**: Detect contradictions between generated facts and ground truth
- **Measure Relevance**: Evaluate how well responses address farmer queries
- **Build Trust**: Provide transparent quality metrics for AI-generated agricultural advice

**Use Cases:**

#### 1. **Specificity Evaluation** (`specificity_evaluation`)

**Purpose**: Classify agricultural facts as "Specific" or "Not Specific" based on contextual anchors (location, time, quantity, entity) and actionability.

**Why It Matters**: Generic advice like "water your plants" is unhelpful. Farmers need specific guidance like "water tomato plants with 2 liters per plant every morning in summer." This prompt ensures facts contain enough detail for real-world application.

**Expected Input**:
```python
{
    "fact_text": "Apply neem oil at 3ml per liter for aphid control",
    "query_context": "User asked about organic pest control for tomatoes",
    "additional_params": "Focus on Bihar farming context"
}
```

**Expected Output**:
```json
{
    "text": "Apply neem oil at 3ml per liter for aphid control",
    "label": "Specific",
    "flags": [
        "entity_specificity",
        "quantity_measurement",
        "actionability"
    ],
    "justification": "Contains specific crop (tomatoes), precise measurement (3ml/L), and clear action (apply for aphid control), enabling farmers to implement directly."
}
```

**When to Use**: After generating facts, before storing them in a knowledge base or presenting to users.

---

#### 2. **Fact Generation** (`fact_generation`)

**Purpose**: Extract atomic, verifiable facts from conversational chatbot responses, filtering out greetings, disclaimers, and non-agricultural content.

**Why It Matters**: Chatbot responses often contain multiple claims mixed with conversational elements. This prompt isolates actionable agricultural knowledge, making it easier to validate, store, and reuse. Each fact becomes a standalone, verifiable unit.

**Expected Input**:
```python
{
    "chatbot_response": "Hello! For aphid control, apply neem oil at 3ml per liter. Spray in early morning. Repeat every 7 days. Hope this helps!",
    "user_query": "How to control aphids organically?",
    "regional_context": "Bihar-specific practices",
    "additional_params": "Extract only organic pest control methods"
}
```

**Expected Output**:
```json
{
    "facts": [
        {
            "fact": "Apply neem oil at 3ml per liter concentration for aphid control",
            "category": "pest_disease",
            "location_dependency": "universal",
            "bihar_relevance": "high",
            "confidence": 0.9
        },
        {
            "fact": "Apply neem oil spray in early morning for optimal effectiveness",
            "category": "pest_disease",
            "location_dependency": "universal",
            "bihar_relevance": "high",
            "confidence": 0.85
        },
        {
            "fact": "Repeat neem oil application every 7 days for persistent aphid control",
            "category": "pest_disease",
            "location_dependency": "universal",
            "bihar_relevance": "high",
            "confidence": 0.9
        }
    ]
}
```

**When to Use**: Immediately after receiving chatbot responses, before any downstream processing.

---

#### 3. **Fact Matching** (`fact_recall`)

**Purpose**: Find semantic matches between predicted facts and ground truth facts, accounting for different wording but equivalent agricultural meaning.

**Why It Matters**: The same agricultural advice can be expressed many ways. "Apply 3ml neem oil per liter" and "Mix neem oil at 3ml/L concentration" convey the same information. This prompt identifies equivalent facts for evaluation metrics like precision and recall.

**Expected Input**:
```python
{
    "category": "pest_disease",
    "gold_fact": "Apply neem oil at 3ml per liter for aphid control",
    "pred_facts": [
        "Use neem oil spray for pest management",
        "Mix 3ml neem oil in 1 liter water for aphids",
        "Water plants regularly"
    ]
}
```

**Expected Output**:
```json
{
    "best_match": "Mix 3ml neem oil in 1 liter water for aphids",
    "reason": "Both facts specify the same concentration (3ml per liter), same pest (aphids), and same treatment method (neem oil), representing equivalent agricultural advice despite different wording.",
    "confidence": 0.92
}
```

**When to Use**: During evaluation pipelines, after extracting facts from model outputs and comparing against ground truth.

---

#### 4. **Contradiction Detection** (`contradiction_detection`)

**Purpose**: Identify contradictions between generated facts and ground truth, with component-level analysis (temperature, humidity, timing, quantity, etc.).

**Why It Matters**: Contradictory advice can harm crops and farmer livelihoods. If ground truth says "water daily in summer" but the model says "avoid daily watering in summer," farmers receive conflicting guidance. This prompt catches such contradictions before they reach users.

**Expected Input**:
```python
{
    "category": "irrigation",
    "gold_fact": "Water tomato plants daily during summer months",
    "pred_facts": [
        "Avoid daily watering in summer to prevent root rot",
        "Water every 2-3 days for optimal growth",
        "Apply mulch to retain moisture"
    ],
    "additional_context": "Focus on tomato cultivation in Bihar"
}
```

**Expected Output**:
```json
{
    "contradictions": [
        {
            "contradicting_fact": "Avoid daily watering in summer to prevent root rot",
            "reference_fact": "Water tomato plants daily during summer months",
            "reason": "Direct opposition on watering frequency: reference recommends daily watering while candidate advises avoiding it.",
            "confidence": "High",
            "components_compared": [
                {
                    "component": "timing",
                    "reference_value": "daily",
                    "candidate_value": "avoid daily",
                    "status": "conflict"
                },
                {
                    "component": "season",
                    "reference_value": "summer",
                    "candidate_value": "summer",
                    "status": "compatible"
                }
            ],
            "structured_justification": [
                "Step 1: Decomposed facts into watering frequency and seasonal components",
                "Step 2: Identified opposite recommendations for frequency (daily vs. avoid daily)",
                "Step 3: Confirmed genuine contradiction in core watering guidance"
            ]
        }
    ]
}
```

**When to Use**: After fact matching, to identify generated facts that conflict with established knowledge.

---

#### 5. **Relevance Evaluation** (`relevance_evaluation`)

**Purpose**: Evaluate unmatched facts for relevance, quality, practical value, and farmer applicability, providing detailed scoring across multiple dimensions.

**Why It Matters**: Not all unmatched facts are bad—some provide valuable complementary information. Others are off-topic. This prompt distinguishes between high-quality additional advice and irrelevant content, helping you decide what to keep, improve, or discard.

**Expected Input**:
```python
{
    "question": "How to control aphids on tomato plants organically?",
    "ground_facts": [
        "Apply neem oil at 3ml per liter",
        "Use yellow sticky traps"
    ],
    "unmatched_facts": [
        "Water plants regularly in morning",
        "Introduce parasitic wasps for biological control",
        "Harvest tomatoes when fully red"
    ],
    "additional_evaluation_criteria": "Prioritize organic pest control methods"
}
```

**Expected Output**:
```json
{
    "question": "How to control aphids on tomato plants organically?",
    "ground_facts": ["Apply neem oil at 3ml per liter", "Use yellow sticky traps"],
    "predicted_facts_analysis": [
        {
            "predicted_fact": "Water plants regularly in morning",
            "relevance_score": 3,
            "ground_truth_alignment_score": 2,
            "practical_value_score": 5,
            "specificity_score": 4,
            "agricultural_soundness_score": 7,
            "overall_score": 4,
            "explanation": "While proper watering is important for plant health, this fact doesn't directly address aphid control, which is the core question.",
            "gaps_identified": [
                "No connection to pest management",
                "Doesn't complement existing organic control methods"
            ],
            "farmer_applicability": "Easy to implement but not relevant to the aphid problem"
        },
        {
            "predicted_fact": "Introduce parasitic wasps for biological control",
            "relevance_score": 9,
            "ground_truth_alignment_score": 8,
            "practical_value_score": 8,
            "specificity_score": 7,
            "agricultural_soundness_score": 9,
            "overall_score": 8,
            "explanation": "Highly relevant organic pest control method that complements neem oil and sticky traps. Parasitic wasps are effective natural predators of aphids.",
            "gaps_identified": [
                "Could specify wasp species (e.g., Aphidius colemani)",
                "Release timing not mentioned"
            ],
            "farmer_applicability": "Moderate implementation - requires sourcing beneficial insects, but highly effective for organic farming"
        }
    ],
    "summary": {
        "total_predicted_facts": 3,
        "average_overall_score": 6.3,
        "key_insights": [
            "One fact (parasitic wasps) provides valuable complementary pest control",
            "Two facts are tangential to the core aphid control question"
        ],
        "recommendations": [
            "Keep parasitic wasp fact as additional organic control option",
            "Consider removing or rephrasing watering and harvest facts"
        ]
    }
}
```

**When to Use**: At the end of the evaluation pipeline, to assess facts that didn't match ground truth but might still be valuable.

Here is the `fact_stitching` section formatted exactly like the other use cases in the documentation (matching `relevance_evaluation`, `contradiction_detection`, etc.).

#### 6. **Fact Stitching** (`fact_stitching`)

**Purpose**: Synthesize structured atomic facts into natural, conversational, and empathetic responses suitable for farmers.

**Why It Matters**: Raw data and atomic facts can feel robotic and disconnected. Farmers trust advice that sounds like it comes from an expert who understands their context. This prompt turns dry data into a "human" conversation, adding necessary transitions, cultural tone, and educational context without hallucinating new information.

**Expected Input**:

```python
{
    "original_query": "How to control aphids organically?",
    "facts_json": [
        {
            "fact": "Apply neem oil at 3ml per liter for aphid control",
            "category": "pest_disease",
            "confidence": 0.9,
            "bihar_relevance": "high"
        },
        {
            "fact": "Spray in early morning for best effectiveness",
            "category": "pest_disease",
            "confidence": 0.85,
            "bihar_relevance": "high"
        }
    ],
    "additional_context": "Tone should be encouraging and focus on Bihar context."
}

```

**Expected Output** (Text Response):

```text
"To control aphids organically, I recommend using Neem oil, which is a very effective natural solution. You should mix neem oil at a concentration of 3ml per liter of water.

For the best results, please spray this mixture in the early morning. This helps ensure the solution stays on the plants longer and works better against the pests. This is a widely accepted practice for farmers in Bihar to protect their crops safely."

```

**When to Use**: The final step of a RAG pipeline, after retrieving and verifying facts, just before sending the answer to the user.

#### 7. Conversationality Evaluation (conversationality_eval_for_stitching)
**Purpose**: Evaluate synthesized agricultural responses against Farmer.CHAT guidelines for conversationality, practicality, and farmer-friendliness.

**Why It Matters:** Even factually correct answers can be bad if they are robotic, condescending, or culturally inappropriate. This prompt acts as a "Quality Assurance" agent, scoring the response on:

- Content Quality: Is it actionable?

- Communication Style: Is it warm and professional?

- Practical Advice: Is it low-cost and accessible?

- Safety & Credibility: Are chemical precautions included?

- Conversation Flow: Does it feel natural?

- Response Format: Is it structured well?

**Expected Input**:
```python
{
    "question": "How do I use neem oil?",
    "response": "To use neem oil, mix 5ml per liter...",
    "chat_history": "[Previous turn...]",
    "additional_context": "Farmer is from Bihar"
}
```

**Expected Output**:
```python
{
   "content_quality": { "score": 5, "justification": "...", "examples": [...] },
   "communication_style": { "score": 4, "justification": "...", "examples": [...] },
   "overall_score": 4.5,
   "overall_assessment": "Excellent practical advice with a warm tone."
}
```

**When to Use**: As a final check on stitched responses before sending them to the user, or for offline quality benchmarking.

---

## Advanced Usage

### Crop Advisory Example

```python
from farmerchat_prompts import PromptManager

manager = PromptManager()

# Get pest management prompt
prompt = manager.get_prompt("openai", "pest_management", "crop_advisory")

# Format with farmer's data
user_input = """
My tomato plants have yellow spots on leaves.
About 30% of plants affected.
Noticed 5 days ago in Patna, Bihar.
"""

# Get full prompt for API
full_prompt = prompt.get_full_prompt(user_input)

# Call OpenAI API
from openai import OpenAI
client = OpenAI(api_key="your-key")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": full_prompt["system"]},
        *full_prompt["messages"]
    ],
    max_tokens=2000
)
```

### Custom Variables

```python
prompt = manager.get_prompt("openai", "weather_advisory", "crop_advisory")

# Format with custom variables
formatted = prompt.format(
    location="Araria, Bihar",
    current_weather="Heavy rainfall expected",
    crops="Rice, Wheat",
    growth_stage="Flowering",
    planned_activities="Pesticide spraying",
    concerns="Rain damage"
)
```

### Validation

```python
# Check if a combination exists
exists = manager.validate_combination("openai", "crop_recommendation", "crop_advisory")

# Get metadata
metadata = prompt.metadata
print(f"Provider: {metadata.provider}")
print(f"Use Case: {metadata.use_case}")
print(f"Domain: {metadata.domain}")
print(f"Version: {metadata.version}")
```

## Prompt Engineering Details

Each provider has specific optimizations:

### OpenAI Prompts
- **Style**: Structured with clear system/user roles, concise instructions
- **Length**: 200-500 words for system prompts
- **Format**: Bulleted lists, numbered steps, clear JSON output schemas
- **Best for**: Fast responses, structured outputs, function calling

### Llama Prompts
- **Style**: Direct instructions, example-driven learning
- **Length**: 300-800 words with extensive examples
- **Format**: `[INST]`, `<<SYS>>` formatting
- **Best for**: Local deployment, cost-effective, privacy-focused

### Gemma Prompts
- **Style**: Instruction-tuned, compact
- **Format**: Uses `<start_of_turn>` and `<end_of_turn>` special tokens. System instructions are merged into the first user turn.
- **Best for**: Efficient local inference, Google Cloud Vertex AI

## Development

### Setup

```bash
git clone https://github.com/digitalgreenorg/farmerchat-prompts
cd farmerchat-prompts
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black farmerchat_prompts/
flake8 farmerchat_prompts/
```

## Package Statistics

- **Total Prompts**: 36 (15 crop advisory + 21 prompt evals across Providers)
- **Providers**: 3 (OpenAI, Llama, Gemma)
- **Domains**: 2 (crop_advisory, prompt_evals)
- **Use Cases**: 12 (5 crop advisory + 7 prompt evals)
- **Code Lines**: 3,500+
- **Test Coverage**: 33+ test cases

## Architecture

```
farmerchat_prompts/
├── models.py           # Pydantic models with Domain support
├── manager.py          # PromptManager with domain parameter
└── prompts/
    ├── crop_advisory/  # Agricultural guidance prompts
    │   ├── openai.py   # 5 prompts
    │   ├── gemma.py   # 5 prompts
    │   └── llama.py    # 5 prompts
    └── prompt_evals/   # Evaluation & extraction prompts
        ├── openai.py   # 7 prompts
        └── llama.py    # 7 prompts
        └── gemma.py    # 7 prompts
```

## Backward Compatibility

Existing code works without changes - domain parameter defaults to `crop_advisory`:

```python
# Old code (still works)
prompt = manager.get_prompt("openai", "crop_recommendation")

# Equivalent to new code
prompt = manager.get_prompt("openai", "crop_recommendation", "crop_advisory")
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

### Adding a New Domain

1. Create new directory: `prompts/your_domain/`
2. Add provider files: `openai.py`, `gemma.py`, `llama.py`
3. Update `Domain` enum in `models.py`
4. Update `UseCase` enum with new use cases
5. Update `manager.py` to load new domain
6. Add tests for new domain

## Support & Resources

- **Documentation**: Full docs in this README
- **Examples**: See `examples/usage_examples.py`
- **Issues**: GitHub Issues
- **Email**: aakash@digitalgreen.org

## License

MIT License - see LICENSE file for details

## Citation

If you use this package in your research or production system, please cite:

```bibtex
@software{farmerchat_prompts,
  author = {aakash@digitalgreen.org},
  title = {FarmerChat Prompts: Multi-Domain AI Prompt Management for Agriculture},
  year = {2024},
  url = {https://github.com/digitalgreenorg/farmerchat-prompts}
}
```

## Acknowledgments

- Built for Farmer.Chat agricultural AI platform
- Optimized for Indian farming contexts
- Follows prompt engineering best practices from OpenAI, Google and Meta
- Includes comprehensive prompt evaluation framework for quality assessment

---

**Version**: 0.2.0  
**Last Updated**: December 2025 
