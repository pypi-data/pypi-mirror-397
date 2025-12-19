"""
Example usage of farmerchat-prompts package with multi-domain support

This script demonstrates how to use the package with different AI providers
across multiple domains (crop_advisory and prompt_evals)
"""

from farmerchat_prompts import PromptManager, Provider, UseCase, Domain
import json


def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    # Initialize the manager
    manager = PromptManager()
    
    # Get a specific prompt from crop_advisory domain
    prompt = manager.get_prompt("openai", "crop_recommendation")
    
    print(f"Provider: {prompt.metadata.provider.value}")
    print(f"Use Case: {prompt.metadata.use_case.value}")
    print(f"Domain: {prompt.metadata.domain.value}")
    print(f"Description: {prompt.metadata.description}")
    print(f"\nSystem Prompt Preview: {prompt.system_prompt[:200]}...")
    print(f"\nAvailable Variables: {list(prompt.variables.keys())}")


def example_with_openai_crop_advisory():
    """Example with OpenAI for crop advisory"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: OpenAI - Crop Advisory")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt("openai", "crop_recommendation", "crop_advisory")
    
    # Prepare the full prompt for API call
    user_input = """I have a 2-acre farm in Araria, Bihar. 
    Soil is sandy loam with pH 6.5. 
    Canal irrigation is available. 
    I want to grow crops in the kharif season."""
    
    full_prompt = prompt.get_full_prompt(user_input)
    
    print("Ready for OpenAI API call:")
    print(f"Domain: {prompt.metadata.domain.value}")
    print(f"Messages structure: {type(full_prompt['messages'])}")
    print(f"Number of messages: {len(full_prompt['messages'])}")
    
    # Example API call (commented out - requires API key)
    """
    import openai
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=full_prompt["messages"]
    )
    print(response.choices[0].message.content)
    """


def example_with_openai_prompt_evals():
    """Example with OpenAI for prompt evaluation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: OpenAI - Prompt Evaluation (Specificity)")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt(
        provider="openai",
        use_case="specificity_evaluation",
        domain="prompt_evals"
    )
    
    print(f"Domain: {prompt.metadata.domain.value}")
    print(f"Use Case: {prompt.metadata.use_case.value}")
    print(f"Description: {prompt.metadata.description}")
    
    # Format with specific parameters
    formatted = prompt.user_prompt_template.format(
        fact_text="Apply neem oil at 3ml per liter concentration for aphid control",
        query_context="User asked: How to control aphids on tomato plants organically?",
        additional_params="Focus on actionability for Bihar farmers"
    )
    
    print(f"\nFormatted prompt preview:")
    print(formatted[:300] + "...")
    
    # Example API call (commented out)
    """
    import openai
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt.system_prompt},
            {"role": "user", "content": formatted}
        ],
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    print(f"Label: {result['label']}")
    print(f"Justification: {result['justification']}")
    """


def example_fact_generation():
    """Example of fact generation from prompt_evals domain"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Fact Generation from Chatbot Response")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt(
        provider="openai",
        use_case="fact_generation",
        domain="prompt_evals"
    )
    
    chatbot_response = """
    For aphid control on tomatoes, I recommend applying neem oil spray. 
    Mix 3ml of neem oil per liter of water. Apply early in the morning 
    for best results. Repeat the application every 7 days during the 
    flowering stage for persistent control.
    """
    
    formatted = prompt.user_prompt_template.format(
        chatbot_response=chatbot_response,
        user_query="How to control aphids on tomato organically?",
        regional_context="Bihar-specific farming practices",
        additional_params="Extract only actionable facts with measurements"
    )
    
    print("Ready to extract facts from chatbot response")
    print(f"Response length: {len(chatbot_response)} chars")
    
    # Example output structure
    print("\nExpected output structure:")
    print(json.dumps({
        "facts": [
            {
                "fact": "Apply neem oil at 3ml per liter concentration",
                "category": "pest_disease",
                "location_dependency": "universal",
                "bihar_relevance": "high",
                "confidence": 0.9
            }
        ]
    }, indent=2))


def example_fact_recall():
    """Example of semantic fact recall"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Semantic Fact Matching")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt(
        provider="openai",
        use_case="fact_recall",
        domain="prompt_evals"
    )
    
    gold_fact = "Apply neem oil at 3ml per liter for aphid control"
    candidate_facts = [
        "Use neem oil spray for pest management",
        "Mix 3ml neem oil in 1 liter water for aphids",
        "Water the plants regularly"
    ]
    
    formatted = prompt.user_prompt_template.format(
        category="pest_disease",
        gold_fact=gold_fact,
        pred_facts=json.dumps(candidate_facts, indent=2)
    )
    
    print(f"Gold fact: {gold_fact}")
    print(f"Comparing against {len(candidate_facts)} candidates")
    
    # Expected to find candidate_facts[1] as best match
    print("\nExpected best match: 'Mix 3ml neem oil in 1 liter water for aphids'")
    print("Expected confidence: > 0.9")


def example_contradiction_detection():
    """Example of contradiction detection"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Contradiction Detection")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt(
        provider="openai",
        use_case="contradiction_detection",
        domain="prompt_evals"
    )
    
    reference_fact = "Water tomato plants daily during summer"
    candidate_facts = [
        "Avoid daily watering in summer to prevent root rot",
        "Water every 2-3 days for best results",
        "Apply mulch to retain moisture"
    ]
    
    formatted = prompt.user_prompt_template.format(
        category="irrigation",
        gold_fact=reference_fact,
        pred_facts=json.dumps(candidate_facts),
        additional_context="Focus on tomato cultivation practices"
    )
    
    print(f"Reference: {reference_fact}")
    print(f"Checking {len(candidate_facts)} facts for contradictions")
    
    # First two facts contradict the reference
    print("\nExpected contradictions: 2")
    print("- Fact 1: Contradicts watering frequency")
    print("- Fact 2: Contradicts daily timing")


def example_relevance_evaluation():
    """Example of relevance evaluation"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Relevance Evaluation")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt(
        provider="openai",
        use_case="relevance_evaluation",
        domain="prompt_evals"
    )
    
    question = "How to control aphids on tomato plants organically?"
    ground_facts = [
        "Apply neem oil spray at 3ml per liter",
        "Use yellow sticky traps to catch adult aphids"
    ]
    unmatched_facts = [
        "Water plants regularly in morning",
        "Tomatoes need 6-8 hours of sunlight",
        "Introduce ladybugs as natural predators"
    ]
    
    formatted = prompt.user_prompt_template.format(
        question=question,
        ground_facts=json.dumps(ground_facts),
        unmatched_facts=json.dumps(unmatched_facts),
        additional_evaluation_criteria="Prioritize organic pest control methods"
    )
    
    print(f"Question: {question}")
    print(f"Ground facts: {len(ground_facts)}")
    print(f"Evaluating {len(unmatched_facts)} unmatched facts")
    
    print("\nExpected relevance scores:")
    print("- 'Water plants regularly' - Low relevance (3-4/10)")
    print("- 'Sunlight requirement' - Low relevance (2-3/10)")
    print("- 'Ladybugs as predators' - High relevance (8-9/10)")

def example_fact_stitching():
    """Example of synthesizing facts into natural responses"""
    print("\n" + "=" * 60)
    print("EXAMPLE 14: Fact Stitching (Synthesis)")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt("openai", "fact_stitching", "prompt_evals")
    
    # Structured facts from previous extraction
    facts = [
        {
            "fact": "Apply neem oil at 3ml per liter concentration for aphid control",
            "category": "pest_disease",
            "confidence": 0.9,
            "bihar_relevance": "high"
        },
        {
            "fact": "Spray neem oil in early morning for best effectiveness",
            "category": "pest_disease",
            "confidence": 0.85,
            "bihar_relevance": "high"
        },
        {
            "fact": "Repeat application every 7 days during flowering stage",
            "category": "pest_disease",
            "confidence": 0.9,
            "bihar_relevance": "high"
        },
        {
            "fact": "Introduce ladybugs as natural predators for aphids",
            "category": "pest_disease",
            "confidence": 0.85,
            "bihar_relevance": "medium"
        }
    ]
    
    formatted = prompt.user_prompt_template.format(
        original_query="How can I control aphids on my tomato plants organically?",
        facts_json=json.dumps(facts, indent=2),
        additional_context="Focus on practical, actionable advice"
    )
    
    print(f"Original query: How can I control aphids on my tomato plants organically?")
    print(f"Facts to synthesize: {len(facts)}")
    print("\nExpected output: Natural, conversational response that:")
    print("  - Addresses the query directly")
    print("  - Weaves facts into cohesive paragraphs")
    print("  - Maintains technical accuracy")
    print("  - Uses farmer-friendly language")
    print("  - Includes practical implementation steps")



def example_exploring_domains():
    """Example of exploring available domains"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Exploring Domains")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Get statistics
    stats = manager.get_stats()
    print(f"Total prompts: {stats['total_prompts']}")
    print(f"Providers: {stats['providers']}")
    print(f"Use cases: {stats['use_cases']}")
    
    # List all domains
    domains = manager.get_available_domains()
    print(f"\nAvailable domains: {domains}")
    
    # Get prompts by domain
    for domain in domains:
        prompts = manager.get_prompts_by_domain(domain)
        print(f"\n{domain.upper()} domain:")
        print(f"  Total prompts: {len(prompts)}")
        
        # Group by provider
        by_provider = {}
        for p in prompts:
            provider = p.metadata.provider.value
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(p.metadata.use_case.value)
        
        for provider, use_cases in by_provider.items():
            print(f"  {provider}: {len(use_cases)} use cases")
            for uc in use_cases:
                print(f"    - {uc}")


def example_complete_matrix():
    """Example showing complete matrix of prompts"""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Complete Prompt Matrix")
    print("=" * 60)
    
    manager = PromptManager()
    
    providers = manager.get_available_providers()
    domains = manager.get_available_domains()
    
    print(f"\n{'Domain':<20} {'Provider':<15} {'Use Cases':<30} {'Available'}")
    print("-" * 80)
    
    for domain in domains:
        domain_prompts = manager.get_prompts_by_domain(domain)
        domain_use_cases = {}
        
        # Group by provider
        for p in domain_prompts:
            provider = p.metadata.provider.value
            if provider not in domain_use_cases:
                domain_use_cases[provider] = []
            domain_use_cases[provider].append(p.metadata.use_case.value)
        
        # Print matrix
        for provider in providers:
            use_cases = domain_use_cases.get(provider, [])
            count = len(use_cases)
            available = "✓" if count > 0 else "✗"
            print(f"{domain:<20} {provider:<15} {count} use cases{' ':<16} {available}")


def example_backward_compatibility():
    """Example showing backward compatibility"""
    print("\n" + "=" * 60)
    print("EXAMPLE 11: Backward Compatibility")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Old API (without domain) - defaults to crop_advisory
    old_style = manager.get_prompt("openai", "crop_recommendation")
    
    # New API (with domain)
    new_style = manager.get_prompt("openai", "crop_recommendation", "crop_advisory")
    
    print("Old API (no domain parameter):")
    print(f"  Domain: {old_style.metadata.domain.value}")
    print(f"  Use Case: {old_style.metadata.use_case.value}")
    
    print("\nNew API (with domain parameter):")
    print(f"  Domain: {new_style.metadata.domain.value}")
    print(f"  Use Case: {new_style.metadata.use_case.value}")
    
    print("\nBoth return the same prompt: ", old_style == new_style)


def example_real_world_eval_pipeline():
    """Example of real-world evaluation pipeline"""
    print("\n" + "=" * 60)
    print("EXAMPLE 12: Real-World Evaluation Pipeline")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Simulate evaluation workflow
    print("Step 1: Generate facts from chatbot response")
    fact_gen = manager.get_prompt("openai", "fact_generation", "prompt_evals")
    print(f"  Using: {fact_gen.metadata.use_case.value}")
    
    print("\nStep 2: Evaluate specificity of each fact")
    specificity = manager.get_prompt("openai", "specificity_evaluation", "prompt_evals")
    print(f"  Using: {specificity.metadata.use_case.value}")
    
    print("\nStep 3: Match generated facts with ground truth")
    matcher = manager.get_prompt("openai", "fact_recall", "prompt_evals")
    print(f"  Using: {matcher.metadata.use_case.value}")
    
    print("\nStep 4: Check for contradictions")
    contradiction = manager.get_prompt("openai", "contradiction_detection", "prompt_evals")
    print(f"  Using: {contradiction.metadata.use_case.value}")
    
    print("\nStep 5: Evaluate relevance of unmatched facts")
    relevance = manager.get_prompt("openai", "relevance_evaluation", "prompt_evals")
    print(f"  Using: {relevance.metadata.use_case.value}")
    
    print("\n✓ Complete evaluation pipeline configured!")


def example_cross_domain_usage():
    """Example using both domains together"""
    print("\n" + "=" * 60)
    print("EXAMPLE 13: Cross-Domain Usage")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Use crop advisory to generate response
    print("1. Generate crop advice using crop_advisory domain:")
    crop_prompt = manager.get_prompt("openai", "pest_management", "crop_advisory")
    print(f"   Prompt: {crop_prompt.metadata.use_case.value}")
    print(f"   Domain: {crop_prompt.metadata.domain.value}")
    
    # Simulate getting a response
    simulated_response = "Apply neem oil spray at 3ml per liter in early morning..."
    
    # Evaluate the response using prompt_evals
    print("\n2. Extract facts using prompt_evals domain:")
    fact_gen = manager.get_prompt("openai", "fact_generation", "prompt_evals")
    print(f"   Prompt: {fact_gen.metadata.use_case.value}")
    print(f"   Domain: {fact_gen.metadata.domain.value}")
    
    print("\n3. Evaluate fact specificity:")
    specificity = manager.get_prompt("openai", "specificity_evaluation", "prompt_evals")
    print(f"   Prompt: {specificity.metadata.use_case.value}")
    print(f"   Domain: {specificity.metadata.domain.value}")
    
    print("\n✓ Cross-domain workflow: crop_advisory → prompt_evals")
    
def example_conversationality_eval():
    """Example of evaluating conversational quality"""
    print("\n" + "=" * 60)
    print("EXAMPLE 15: Conversationality Evaluation")
    print("=" * 60)
    
    manager = PromptManager()
    prompt = manager.get_prompt(
        provider="openai", 
        use_case="conversationality_eval_for_stitching", 
        domain="prompt_evals"
    )
    
    stitched_response = """
    To control aphids, apply neem oil at 3ml per liter. 
    Do this in the early morning for best results. 
    It is important to repeat this every 7 days.
    """
    
    formatted = prompt.user_prompt_template.format(
        question="How to control aphids?",
        response=stitched_response,
        chat_history="User asked about tomatoes previously.",
        additional_context="Farmer is from Bihar."
    )
    
    print(f"Evaluating stitched response quality...")
    print(f"Response length: {len(stitched_response)} chars")
    print(f"Use Case: {prompt.metadata.use_case.value}")
    print("Expected Output: JSON score object for 'content_quality', 'communication_style', etc.")


def example_with_gemma():
    """Example using the Gemma provider"""
    print("\n" + "=" * 60)
    print("EXAMPLE 16: Using with Gemma")
    print("=" * 60)
    
    manager = PromptManager()
    
    # Get a Gemma prompt from prompt_evals
    try:
        prompt = manager.get_prompt("gemma", "fact_generation", "prompt_evals")
        
        user_input = "Extract facts from: Apply 3ml neem oil per liter."
        
        # Get full prompt with Gemma tokens
        full_prompt = prompt.get_full_prompt(user_input)
        
        print(f"Provider: {prompt.metadata.provider.value}")
        print("Ready for Gemma Inference:")
        
        # Displaying how the prompt is formatted for Gemma
        # Note: It should contain <start_of_turn> tags
        print(f"Prompt starts with: {full_prompt['prompt'][:100]}...")
        if "<start_of_turn>user" in full_prompt['prompt']:
            print("✓ Correctly formatted with <start_of_turn>user tags")
        
    except ValueError:
        print("Gemma prompts not yet loaded or implemented in this environment.")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_with_openai_crop_advisory()
    example_with_openai_prompt_evals()
    example_fact_generation()
    example_fact_recall()
    example_contradiction_detection()
    example_relevance_evaluation()
    example_exploring_domains()
    example_complete_matrix()
    example_backward_compatibility()
    example_real_world_eval_pipeline()
    example_cross_domain_usage()
    example_fact_stitching()
    example_conversationality_eval()
    example_with_gemma()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)