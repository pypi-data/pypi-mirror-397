"""
Tests for farmerchat-prompts package with multi-domain support
"""

import pytest
from farmerchat_prompts import PromptManager, Provider, UseCase, Domain


class TestPromptManager:
    """Test cases for PromptManager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_initialization(self):
        """Test manager initializes correctly"""
        assert self.manager is not None
        stats = self.manager.get_stats()
        assert stats["total_prompts"] >= 15  # At least crop advisory prompts
        assert stats["providers"] == 3
    
    def test_get_prompt_valid(self):
        """Test getting valid prompt"""
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        assert prompt is not None
        assert prompt.metadata.provider == Provider.OPENAI
        assert prompt.metadata.use_case == UseCase.CROP_RECOMMENDATION
    
    def test_get_prompt_with_enums(self):
        """Test getting prompt with enum values"""
        prompt = self.manager.get_prompt(
            Provider.OPENAI, 
            UseCase.PEST_MANAGEMENT
        )
        assert prompt is not None
        assert prompt.metadata.provider == Provider.OPENAI
    
    def test_get_prompt_invalid_provider(self):
        """Test getting prompt with invalid provider"""
        with pytest.raises(ValueError, match="Provider 'invalid' not found"):
            self.manager.get_prompt("invalid", "crop_recommendation")
    
    def test_get_prompt_invalid_use_case(self):
        """Test getting prompt with invalid use case"""
        with pytest.raises(ValueError, match="Use case 'invalid' not found"):
            self.manager.get_prompt("openai", "invalid")
    
    def test_get_prompts_by_provider(self):
        """Test getting all prompts for a provider"""
        prompts = self.manager.get_prompts_by_provider("openai")
        assert len(prompts) >= 5  # At least crop advisory prompts
        assert all(p.metadata.provider == Provider.OPENAI for p in prompts)
    
    def test_get_prompts_by_use_case(self):
        """Test getting all prompts for a use case"""
        prompts = self.manager.get_prompts_by_use_case("crop_recommendation")
        assert len(prompts) == 3  # One for each provider
        assert all(
            p.metadata.use_case == UseCase.CROP_RECOMMENDATION 
            for p in prompts
        )
    
    def test_list_all_prompts(self):
        """Test listing all prompt combinations"""
        all_prompts = self.manager.list_all_prompts()
        assert len(all_prompts) >= 15
        
        # Check structure
        first = all_prompts[0]
        assert "provider" in first
        assert "use_case" in first
    
    def test_validate_combination(self):
        """Test validation of provider/use_case combinations"""
        assert self.manager.validate_combination("openai", "crop_recommendation")
        assert self.manager.validate_combination(Provider.OPENAI, UseCase.SOIL_ANALYSIS)
        assert not self.manager.validate_combination("openai", "invalid")
        assert not self.manager.validate_combination("invalid", "crop_recommendation")
    
    def test_get_available_providers(self):
        """Test getting list of providers"""
        providers = self.manager.get_available_providers()
        assert len(providers) == 3
        assert "openai" in providers
        assert "gemma" in providers
        assert "llama" in providers
    
    def test_get_available_use_cases(self):
        """Test getting list of use cases"""
        use_cases = self.manager.get_available_use_cases()
        assert len(use_cases) >= 5
        assert "crop_recommendation" in use_cases
        assert "pest_management" in use_cases
        
        # Test filtering by provider
        openai_cases = self.manager.get_available_use_cases("openai")
        assert len(openai_cases) >= 5
    
    def test_search_prompts(self):
        """Test searching prompts by keyword"""
        # Search in description
        results = self.manager.search_prompts("pest")
        assert len(results) >= 3  # At least one per provider
        
        # Search in tags
        results = self.manager.search_prompts("soil")
        assert len(results) >= 3
        
        # No results
        results = self.manager.search_prompts("nonexistent")
        assert len(results) == 0


class TestPrompt:
    """Test cases for Prompt model"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
        self.prompt = self.manager.get_prompt("openai", "crop_recommendation")
    
    def test_prompt_structure(self):
        """Test prompt has required fields"""
        assert self.prompt.metadata is not None
        assert self.prompt.system_prompt is not None
        assert self.prompt.user_prompt_template is not None
        assert isinstance(self.prompt.variables, dict)
    
    def test_format_method(self):
        """Test prompt formatting"""
        formatted = self.prompt.format(
            location="Bihar",
            soil_type="Loamy",
            soil_ph="6.5",
            climate="Tropical",
            water_availability="High",
            farm_size="2 acres",
            additional_info="Planning for kharif season"
        )
        assert "Bihar" in formatted
        assert "Loamy" in formatted
        assert "6.5" in formatted
    
    def test_get_full_prompt_openai(self):
        """Test getting full prompt for OpenAI"""
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        full = prompt.get_full_prompt("I have sandy soil, what should I grow?")
        
        assert "messages" in full
        assert len(full["messages"]) == 2
        assert full["messages"][0]["role"] == "system"
        assert full["messages"][1]["role"] == "user"
    
    def test_get_full_prompt_gemma(self):
        """Test getting full prompt for Gemma"""
        prompt = self.manager.get_prompt("gemma", "crop_recommendation")
        full = prompt.get_full_prompt("I need crop recommendations")
        
        assert "system" in full
        assert "messages" in full
        assert full["messages"][0]["role"] == "user"
    
    def test_get_full_prompt_llama(self):
        """Test getting full prompt for Llama"""
        prompt = self.manager.get_prompt("llama", "crop_recommendation")
        full = prompt.get_full_prompt("What crops should I grow?")
        
        assert "prompt" in full
        assert "User:" in full["prompt"]
        assert "Assistant:" in full["prompt"]


class TestProviderSpecificPrompts:
    """Test provider-specific prompt characteristics"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_openai_prompt_style(self):
        """Test OpenAI prompts follow expected style"""
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        
        # Should have clear system prompt
        assert len(prompt.system_prompt) > 100
        assert "expert" in prompt.system_prompt.lower()
        
        # Should have user template
        assert "{location}" in prompt.user_prompt_template
        assert "{soil_type}" in prompt.user_prompt_template
    
    def test_gemma_prompt_style(self):
        """Test Gemma prompts follow expected style (XML tags)"""
        prompt = self.manager.get_prompt("gemma", "crop_recommendation")
        
        # Should use XML tags
        assert "<role>" in prompt.system_prompt or "<expertise>" in prompt.system_prompt
        assert "<" in prompt.system_prompt and ">" in prompt.system_prompt
        
        # Should have detailed structure
        assert len(prompt.system_prompt) > 500
    
    def test_llama_prompt_style(self):
        """Test Llama prompts follow expected style (direct instructions)"""
        prompt = self.manager.get_prompt("llama", "crop_recommendation")
        
        # Should have clear ROLE and INSTRUCTIONS
        assert "ROLE:" in prompt.system_prompt
        assert "INSTRUCTIONS:" in prompt.system_prompt or "EXAMPLE" in prompt.system_prompt
        
        # Should be example-driven
        assert "EXAMPLE" in prompt.system_prompt


class TestUseCaseCoverage:
    """Test that all use cases are properly covered"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_all_crop_advisory_use_cases_have_all_providers(self):
        """Test each crop advisory use case has prompts for all providers"""
        use_cases = [
            "crop_recommendation",
            "pest_management", 
            "soil_analysis",
            "weather_advisory",
            "market_insights"
        ]
        providers = ["openai", "gemma", "llama"]
        
        for use_case in use_cases:
            prompts = self.manager.get_prompts_by_use_case(use_case)
            assert len(prompts) == 3, f"{use_case} missing providers"
            
            provider_names = {p.metadata.provider.value for p in prompts}
            assert provider_names == set(providers)
    
    def test_all_providers_have_crop_advisory_use_cases(self):
        """Test each provider has prompts for all crop advisory use cases"""
        use_cases = {
            "crop_recommendation",
            "pest_management", 
            "soil_analysis",
            "weather_advisory",
            "market_insights"
        }
        providers = ["openai", "gemma", "llama"]
        
        for provider in providers:
            prompts = self.manager.get_prompts_by_provider(provider)
            # Should have at least 5 crop advisory prompts
            assert len(prompts) >= 5, f"{provider} missing use cases"


class TestDomainSupport:
    """Test domain functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_get_prompt_with_domain(self):
        """Test getting prompt with domain specification"""
        # Crop advisory
        crop_prompt = self.manager.get_prompt(
            "openai", 
            "crop_recommendation",
            "crop_advisory"
        )
        assert crop_prompt.metadata.domain == Domain.CROP_ADVISORY
        
        # Prompt evals (if available)
        try:
            eval_prompt = self.manager.get_prompt(
                "openai",
                "specificity_evaluation", 
                "prompt_evals"
            )
            assert eval_prompt.metadata.domain == Domain.PROMPT_EVALS
        except ValueError:
            # Prompt evals may not be implemented for all providers yet
            pass
    
    def test_backward_compatibility(self):
        """Test that old API still works"""
        # Should default to crop_advisory
        prompt = self.manager.get_prompt("openai", "crop_recommendation")
        assert prompt.metadata.domain == Domain.CROP_ADVISORY
    
    def test_get_available_domains(self):
        """Test getting list of available domains"""
        domains = self.manager.get_available_domains()
        assert isinstance(domains, list)
        assert "crop_advisory" in domains
        # prompt_evals may or may not be available depending on implementation
    
    def test_get_prompts_by_domain(self):
        """Test getting all prompts in a domain"""
        crop_prompts = self.manager.get_prompts_by_domain("crop_advisory")
        assert len(crop_prompts) >= 15  # 3 providers × 5 use cases
        assert all(p.metadata.domain == Domain.CROP_ADVISORY for p in crop_prompts)
    
    def test_domain_in_stats(self):
        """Test that stats include domain count"""
        stats = self.manager.get_stats()
        assert "total_prompts" in stats
        assert stats["providers"] == 3
        # Should have at least crop_advisory domain
        domains = self.manager.get_available_domains()
        assert len(domains) >= 1


class TestPromptEvalsDomain:
    """Test prompt_evals domain prompts (OpenAI implementation)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = PromptManager()
    
    def test_prompt_evals_prompts_exist(self):
        """Test all prompt_evals use cases are available for OpenAI"""
        eval_use_cases = [
            "specificity_evaluation",
            "fact_generation",
            "fact_recall",
            "contradiction_detection",
            "relevance_evaluation"
        ]
        
        for use_case in eval_use_cases:
            try:
                prompt = self.manager.get_prompt("openai", use_case, "prompt_evals")
                assert prompt is not None
                assert prompt.metadata.domain == Domain.PROMPT_EVALS
                assert prompt.metadata.provider == Provider.OPENAI
            except ValueError:
                pytest.skip(f"Prompt eval use case {use_case} not yet implemented")
    
    def test_specificity_evaluator_structure(self):
        """Test specificity evaluator has correct structure"""
        try:
            prompt = self.manager.get_prompt(
                "openai", 
                "specificity_evaluation", 
                "prompt_evals"
            )
            
            # Check required variables
            assert "fact_text" in prompt.variables
            assert "query_context" in prompt.variables
            assert "additional_params" in prompt.variables
            
            # Check system prompt mentions classification
            assert "classify" in prompt.system_prompt.lower() or "classification" in prompt.system_prompt.lower()
            assert "specific" in prompt.system_prompt.lower()
            
        except ValueError:
            pytest.skip("Specificity evaluator not yet implemented")
    
    def test_fact_generator_structure(self):
        """Test fact generator has correct structure"""
        try:
            prompt = self.manager.get_prompt(
                "openai",
                "fact_generation",
                "prompt_evals"
            )
            
            # Check required variables
            assert "chatbot_response" in prompt.variables
            assert "user_query" in prompt.variables
            
            # Check system prompt mentions facts
            assert "fact" in prompt.system_prompt.lower()
            assert "extract" in prompt.system_prompt.lower() or "generat" in prompt.system_prompt.lower()
            
        except ValueError:
            pytest.skip("Fact generator not yet implemented")
    
    def test_fact_recall_structure(self):
        """Test fact recall has correct structure"""
        try:
            prompt = self.manager.get_prompt(
                "openai",
                "fact_recall",
                "prompt_evals"
            )
            
            # Check required variables
            assert "gold_fact" in prompt.variables
            assert "pred_facts" in prompt.variables
            assert "category" in prompt.variables
            
            # Check system prompt mentions matching
            assert "match" in prompt.system_prompt.lower()
            
        except ValueError:
            pytest.skip("Fact matcher not yet implemented")
    
    def test_contradiction_detector_structure(self):
        """Test contradiction detector has correct structure"""
        try:
            prompt = self.manager.get_prompt(
                "openai",
                "contradiction_detection",
                "prompt_evals"
            )
            
            # Check required variables
            assert "gold_fact" in prompt.variables
            assert "pred_facts" in prompt.variables
            
            # Check system prompt mentions contradictions
            assert "contradiction" in prompt.system_prompt.lower()
            
        except ValueError:
            pytest.skip("Contradiction detector not yet implemented")
    
    def test_relevance_evaluator_structure(self):
        """Test relevance evaluator has correct structure"""
        try:
            prompt = self.manager.get_prompt(
                "openai",
                "relevance_evaluation",
                "prompt_evals"
            )
            
            # Check required variables
            assert "question" in prompt.variables
            assert "ground_facts" in prompt.variables
            assert "unmatched_facts" in prompt.variables
            
            # Check system prompt mentions relevance
            assert "relevance" in prompt.system_prompt.lower() or "relevant" in prompt.system_prompt.lower()
            
        except ValueError:
            pytest.skip("Relevance evaluator not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])