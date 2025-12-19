import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.personas import MandatoryPersonas, Persona

# 1. Test Persona Registry Integrity
def test_mandatory_personas_exist():
    personas = MandatoryPersonas.all()
    assert len(personas) == 3
    names = [p.name for p in personas]
    assert "System Architect" in names
    assert "Pragmatic Engineer" in names
    assert "Product Visionary" in names

def test_persona_prompts_not_empty():
    for p in MandatoryPersonas.all():
        assert len(p.system_prompt) > 10
        assert "You are a" in p.system_prompt

# 2. Test Integration with Tools Logic (Mocking LLMManager)
@pytest.mark.asyncio
async def test_round_table_auto_scaling():
    """Verify that fewer than 3 panelists triggers auto-scaling and persona assignment."""
    from src.tools import LLMManager
    
    # Mock dependencies
    manager = LLMManager()
    manager._get_provider = MagicMock()
    manager.logger = MagicMock()
    
    # Mock Provider
    mock_provider = AsyncMock()
    mock_provider.generate_response.return_value = "Mock Draft Content"
    manager._get_provider.return_value = mock_provider
    
    # Mock Session Recorder (Patch where it is defined, not where used if not global)
    with patch("src.persistence.SessionRecorder") as MockRecorder:
        mock_rec_instance = MockRecorder.return_value
        mock_rec_instance.create_session_dir.return_value = "/tmp/mock_session"
        
        # ACT: Call round_table with only 1 panelist
        input_panelists = [{"provider": "openai", "model": "gpt-4o"}]
        
        # We need to test the logic inside round_table_debate. 
        # Since it's a large function, we are essentially running an integration test of the logic block.
        result = await manager.round_table_debate(
            prompt="Test Topic",
            panelists=input_panelists, # Only 1 passed
            moderator_provider="openai"
        )
        
        # ASSERT:
        # 1. Verify provider called 3 times (Auto-scaled from 1 to 3)
        assert mock_provider.generate_response.call_count >= 3 
        
        # 2. Verify Persona System Prompts were passed
        # The args validation is complex because they are async calls gathered.
        # But we can check that at least one call had the "System Architect" prompt.
        calls = mock_provider.generate_response.call_args_list
        architect_prompt = MandatoryPersonas.SYSTEM_ARCHITECT.system_prompt
        
        found_architect = any(
            call.kwargs.get("system_prompt") == architect_prompt 
            for call in calls
        )
        assert found_architect, "System Architect prompt was not injected!"
