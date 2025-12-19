"""
Prompt Manager - Central interface for accessing prompts with multi-domain support
"""

from typing import Dict, List, Optional, Union
from .models import Prompt, Provider, UseCase, Domain


class PromptManager:
    """
    Central manager for accessing and managing AI prompts across providers and domains
    
    Usage:
        manager = PromptManager()
        
        # Backward compatible (defaults to crop_advisory)
        prompt = manager.get_prompt("openai", "crop_recommendation")
        
        # With explicit domain
        prompt = manager.get_prompt("openai", "specificity_evaluation", "prompt_evals")
        
        messages = prompt.get_full_prompt("I have sandy soil in Bihar")
    """
    
    def __init__(self):
        """Initialize the prompt manager with all available prompts"""
        self._prompts: Dict[str, Dict[str, Dict[str, Prompt]]] = {}
        # Structure: {provider: {domain: {use_case: Prompt}}}
        self._load_prompts()
        
    def _load_prompts(self):
        """Load all prompts into the manager"""
        
        # Load Crop Advisory prompts
        try:
            from .prompts.crop_advisory.openai import OPENAI_PROMPTS as CROP_OPENAI
            self._register_prompts(CROP_OPENAI)
        except ImportError:
            pass
            
        try:
            from .prompts.crop_advisory.llama import LLAMA_PROMPTS as CROP_LLAMA
            self._register_prompts(CROP_LLAMA)
        except ImportError:
            pass

        try:
            from .prompts.crop_advisory.gemma import GEMMA_PROMPTS as CROP_GEMMA
            self._register_prompts(CROP_GEMMA)
        except ImportError:
            pass
        
        # Load Prompt Evals prompts
        try:
            from .prompts.prompt_evals.openai import OPENAI_PROMPT_EVALS_PROMPTS
            self._register_prompts(OPENAI_PROMPT_EVALS_PROMPTS)
        except ImportError:
            pass
            
        try:
            from .prompts.prompt_evals.llama import LLAMA_PROMPT_EVALS_PROMPTS
            if LLAMA_PROMPT_EVALS_PROMPTS:  # Check if not empty
                self._register_prompts(LLAMA_PROMPT_EVALS_PROMPTS)
        except ImportError:
            pass
    
        try:
            from .prompts.prompt_evals.gemma import GEMMA_PROMPT_EVALS_PROMPTS
            if GEMMA_PROMPT_EVALS_PROMPTS:  # Check if not empty
                self._register_prompts(GEMMA_PROMPT_EVALS_PROMPTS)
        except ImportError:
            pass

    def _register_prompts(self, prompts: List[Prompt]):
        """Register a list of prompts into the internal structure"""
        for prompt in prompts:
            provider = prompt.metadata.provider.value
            domain = prompt.metadata.domain.value
            use_case = prompt.metadata.use_case.value
            
            # Initialize nested dictionaries if they don't exist
            if provider not in self._prompts:
                self._prompts[provider] = {}
            if domain not in self._prompts[provider]:
                self._prompts[provider][domain] = {}
            
            # Store the prompt
            self._prompts[provider][domain][use_case] = prompt
    
    def get_prompt(
        self, 
        provider: Union[str, Provider], 
        use_case: Union[str, UseCase],
        domain: Union[str, Domain] = "crop_advisory"  # Default for backward compatibility
    ) -> Prompt:
        """
        Get a specific prompt by provider, use case, and domain
        
        Args:
            provider: Provider name (openai, gemma, llama)
            use_case: Use case name
            domain: Domain name (default: crop_advisory for backward compatibility)
            
        Returns:
            Prompt object
            
        Raises:
            ValueError: If combination doesn't exist
            
        Examples:
            # Backward compatible
            prompt = manager.get_prompt("openai", "crop_recommendation")
            
            # With explicit domain
            prompt = manager.get_prompt("openai", "specificity_evaluation", "prompt_evals")
            
            # Using enums
            prompt = manager.get_prompt(
                Provider.OPENAI, 
                UseCase.PEST_MANAGEMENT,
                Domain.CROP_ADVISORY
            )
        """
        # Convert enums to strings if needed
        provider_str = provider.value if isinstance(provider, Provider) else provider
        use_case_str = use_case.value if isinstance(use_case, UseCase) else use_case
        domain_str = domain.value if isinstance(domain, Domain) else domain
        
        # Validate provider
        if provider_str not in self._prompts:
            available = ", ".join(self._prompts.keys())
            raise ValueError(
                f"Provider '{provider_str}' not found. "
                f"Available providers: {available}"
            )
        
        # Validate domain
        if domain_str not in self._prompts[provider_str]:
            available = ", ".join(self._prompts[provider_str].keys())
            raise ValueError(
                f"Domain '{domain_str}' not found for provider '{provider_str}'. "
                f"Available domains: {available}"
            )
        
        # Validate use case
        if use_case_str not in self._prompts[provider_str][domain_str]:
            available = ", ".join(self._prompts[provider_str][domain_str].keys())
            raise ValueError(
                f"Use case '{use_case_str}' not found for provider '{provider_str}' "
                f"in domain '{domain_str}'. Available use cases: {available}"
            )
        
        return self._prompts[provider_str][domain_str][use_case_str]
    
    def get_prompts_by_provider(
        self, 
        provider: Union[str, Provider],
        domain: Optional[Union[str, Domain]] = None
    ) -> List[Prompt]:
        """
        Get all prompts for a specific provider, optionally filtered by domain
        
        Args:
            provider: Provider name
            domain: Optional domain filter
            
        Returns:
            List of Prompt objects
            
        Examples:
            # All prompts for OpenAI
            openai_prompts = manager.get_prompts_by_provider("openai")
            
            # OpenAI prompts only in crop_advisory domain
            crop_openai = manager.get_prompts_by_provider("openai", "crop_advisory")
        """
        provider_str = provider.value if isinstance(provider, Provider) else provider
        
        if provider_str not in self._prompts:
            return []
        
        prompts = []
        
        if domain:
            domain_str = domain.value if isinstance(domain, Domain) else domain
            if domain_str in self._prompts[provider_str]:
                prompts.extend(self._prompts[provider_str][domain_str].values())
        else:
            # Get all prompts across all domains for this provider
            for domain_prompts in self._prompts[provider_str].values():
                prompts.extend(domain_prompts.values())
        
        return prompts
    
    def get_prompts_by_use_case(
        self, 
        use_case: Union[str, UseCase],
        domain: Optional[Union[str, Domain]] = None
    ) -> List[Prompt]:
        """
        Get all prompts for a specific use case across providers, optionally filtered by domain
        
        Args:
            use_case: Use case name
            domain: Optional domain filter
            
        Returns:
            List of Prompt objects
            
        Examples:
            # All crop recommendation prompts across providers
            crop_prompts = manager.get_prompts_by_use_case("crop_recommendation")
            
            # Specificity evaluation prompts in prompt_evals domain
            spec_prompts = manager.get_prompts_by_use_case(
                "specificity_evaluation", 
                "prompt_evals"
            )
        """
        use_case_str = use_case.value if isinstance(use_case, UseCase) else use_case
        domain_str = domain.value if isinstance(domain, Domain) else domain if domain else None
        
        prompts = []
        
        for provider_domains in self._prompts.values():
            if domain_str:
                # Filter by specific domain
                if domain_str in provider_domains:
                    if use_case_str in provider_domains[domain_str]:
                        prompts.append(provider_domains[domain_str][use_case_str])
            else:
                # Search across all domains
                for domain_prompts in provider_domains.values():
                    if use_case_str in domain_prompts:
                        prompts.append(domain_prompts[use_case_str])
        
        return prompts
    
    def get_prompts_by_domain(self, domain: Union[str, Domain]) -> List[Prompt]:
        """
        Get all prompts for a specific domain across all providers
        
        Args:
            domain: Domain name
            
        Returns:
            List of Prompt objects
            
        Example:
            # All prompts in prompt_evals domain
            eval_prompts = manager.get_prompts_by_domain("prompt_evals")
        """
        domain_str = domain.value if isinstance(domain, Domain) else domain
        
        prompts = []
        for provider_domains in self._prompts.values():
            if domain_str in provider_domains:
                prompts.extend(provider_domains[domain_str].values())
        
        return prompts
    
    def list_all_prompts(self) -> List[Dict[str, str]]:
        """
        List all available prompt combinations
        
        Returns:
            List of dicts with provider, domain, and use_case keys
            
        Example:
            all_prompts = manager.list_all_prompts()
            # [
            #   {"provider": "openai", "domain": "crop_advisory", "use_case": "crop_recommendation"},
            #   {"provider": "openai", "domain": "prompt_evals", "use_case": "specificity_evaluation"},
            #   ...
            # ]
        """
        prompts = []
        for provider, domains in self._prompts.items():
            for domain, use_cases in domains.items():
                for use_case in use_cases.keys():
                    prompts.append({
                        "provider": provider,
                        "domain": domain,
                        "use_case": use_case
                    })
        return prompts
    
    def validate_combination(
        self, 
        provider: Union[str, Provider], 
        use_case: Union[str, UseCase],
        domain: Union[str, Domain] = "crop_advisory"
    ) -> bool:
        """
        Check if a provider/use_case/domain combination exists
        
        Args:
            provider: Provider name
            use_case: Use case name
            domain: Domain name (default: crop_advisory)
            
        Returns:
            True if combination exists, False otherwise
            
        Example:
            exists = manager.validate_combination("openai", "crop_recommendation", "crop_advisory")
        """
        try:
            self.get_prompt(provider, use_case, domain)
            return True
        except ValueError:
            return False
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of all available providers
        
        Returns:
            List of provider names
            
        Example:
            providers = manager.get_available_providers()
            # ['openai', 'gemma', 'llama']
        """
        return list(self._prompts.keys())
    
    def get_available_domains(self) -> List[str]:
        """
        Get list of all available domains
        
        Returns:
            List of domain names
            
        Example:
            domains = manager.get_available_domains()
            # ['crop_advisory', 'prompt_evals']
        """
        domains = set()
        for provider_domains in self._prompts.values():
            domains.update(provider_domains.keys())
        return sorted(list(domains))
    
    def get_available_use_cases(
        self, 
        provider: Optional[Union[str, Provider]] = None,
        domain: Optional[Union[str, Domain]] = None
    ) -> List[str]:
        """
        Get list of available use cases, optionally filtered by provider and/or domain
        
        Args:
            provider: Optional provider name to filter by
            domain: Optional domain name to filter by
            
        Returns:
            List of use case names
            
        Examples:
            # All use cases
            all_use_cases = manager.get_available_use_cases()
            
            # Use cases for OpenAI
            openai_use_cases = manager.get_available_use_cases(provider="openai")
            
            # Use cases in prompt_evals domain
            eval_use_cases = manager.get_available_use_cases(domain="prompt_evals")
            
            # Use cases for OpenAI in prompt_evals domain
            specific = manager.get_available_use_cases(
                provider="openai", 
                domain="prompt_evals"
            )
        """
        provider_str = provider.value if isinstance(provider, Provider) else provider if provider else None
        domain_str = domain.value if isinstance(domain, Domain) else domain if domain else None
        
        use_cases = set()
        
        if provider_str:
            # Filter by specific provider
            if provider_str in self._prompts:
                if domain_str:
                    # Filter by specific domain
                    if domain_str in self._prompts[provider_str]:
                        use_cases.update(self._prompts[provider_str][domain_str].keys())
                else:
                    # All domains for this provider
                    for domain_prompts in self._prompts[provider_str].values():
                        use_cases.update(domain_prompts.keys())
        else:
            # All providers
            for provider_domains in self._prompts.values():
                if domain_str:
                    # Filter by specific domain
                    if domain_str in provider_domains:
                        use_cases.update(provider_domains[domain_str].keys())
                else:
                    # All domains
                    for domain_prompts in provider_domains.values():
                        use_cases.update(domain_prompts.keys())
        
        return sorted(list(use_cases))
    
    def search_prompts(
        self, 
        keyword: str,
        domain: Optional[Union[str, Domain]] = None
    ) -> List[Prompt]:
        """
        Search prompts by keyword in description or tags, optionally filtered by domain
        
        Args:
            keyword: Keyword to search for
            domain: Optional domain filter
            
        Returns:
            List of matching Prompt objects
            
        Examples:
            # Search all domains
            pest_prompts = manager.search_prompts("pest")
            
            # Search only in crop_advisory domain
            crop_pest = manager.search_prompts("pest", "crop_advisory")
        """
        keyword_lower = keyword.lower()
        domain_str = domain.value if isinstance(domain, Domain) else domain if domain else None
        matching_prompts = []
        
        for provider_domains in self._prompts.values():
            for current_domain, domain_prompts in provider_domains.items():
                # Skip if domain filter is set and doesn't match
                if domain_str and current_domain != domain_str:
                    continue
                    
                for prompt in domain_prompts.values():
                    # Search in description
                    if keyword_lower in prompt.metadata.description.lower():
                        matching_prompts.append(prompt)
                        continue
                    
                    # Search in tags
                    if any(keyword_lower in tag.lower() for tag in prompt.metadata.tags):
                        matching_prompts.append(prompt)
        
        return matching_prompts
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about available prompts
        
        Returns:
            Dict with counts
            
        Example:
            stats = manager.get_stats()
            # {
            #   "total_prompts": 20, 
            #   "providers": 3, 
            #   "domains": 2,
            #   "use_cases": 10
            # }
        """
        total = 0
        for provider_domains in self._prompts.values():
            for domain_prompts in provider_domains.values():
                total += len(domain_prompts)
        
        return {
            "total_prompts": total,
            "providers": len(self._prompts),
            "domains": len(self.get_available_domains()),
            "use_cases": len(self.get_available_use_cases()),
        }
    
    def get_domain_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Get detailed statistics per domain
        
        Returns:
            Dict with per-domain statistics
            
        Example:
            stats = manager.get_domain_stats()
            # {
            #   "crop_advisory": {"prompts": 15, "providers": 3, "use_cases": 5},
            #   "prompt_evals": {"prompts": 5, "providers": 1, "use_cases": 5}
            # }
        """
        domain_stats = {}
        
        for domain in self.get_available_domains():
            prompts = self.get_prompts_by_domain(domain)
            providers = set(p.metadata.provider.value for p in prompts)
            use_cases = set(p.metadata.use_case.value for p in prompts)
            
            domain_stats[domain] = {
                "prompts": len(prompts),
                "providers": len(providers),
                "use_cases": len(use_cases)
            }
        
        return domain_stats
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"PromptManager("
            f"prompts={stats['total_prompts']}, "
            f"providers={stats['providers']}, "
            f"domains={stats['domains']}, "
            f"use_cases={stats['use_cases']})"
        )