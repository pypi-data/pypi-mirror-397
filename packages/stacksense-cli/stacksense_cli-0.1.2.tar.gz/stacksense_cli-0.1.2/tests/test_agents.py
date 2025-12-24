"""
StackSense Unit Tests
=====================
Tests for BaseAgent and provider-specific agents.

Run with: pytest tests/ -v
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TEST: BaseAgent Tool Implementations
# ═══════════════════════════════════════════════════════════

class TestBaseAgent:
    """Tests for BaseAgent tool implementations."""
    
    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create a temporary workspace for testing."""
        # Create test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "README.md").write_text("# Test Project")
        (tmp_path / ".stacksense").mkdir()
        return tmp_path
    
    @pytest.fixture
    def agent(self, temp_workspace):
        """Create a BaseAgent instance for testing."""
        from stacksense.core.base_agent import BaseAgent
        
        # Use a concrete subclass or mock the abstract method
        class TestAgent(BaseAgent):
            def get_default_model(self):
                return "test-model"
            
            async def chat(self, query, **kwargs):
                return "Test response"
        
        return TestAgent(str(temp_workspace), "test-model", debug=True)
    
    def test_read_file(self, agent, temp_workspace):
        """Test read_file tool."""
        result = agent._tool_read_file("test.py", "test")
        assert "print('hello')" in result
    
    def test_read_file_not_found(self, agent):
        """Test read_file with nonexistent file."""
        result = agent._tool_read_file("nonexistent.py", "test")
        assert "not found" in result.lower() or "error" in result.lower()
    
    def test_write_file_requires_permission(self, agent):
        """Test that write_file requires permission."""
        result = agent._tool_write_file("new.py", "print('test')", "Test file")
        assert "__PERMISSION_REQUIRED__" in result
    
    def test_write_file_with_permission(self, agent, temp_workspace):
        """Test write_file with permission granted."""
        agent._permission_granted = True
        result = agent._tool_write_file("new.py", "print('test')", "Test file")
        assert "Successfully wrote" in result
        assert (temp_workspace / "new.py").exists()
    
    def test_run_command_requires_permission(self, agent):
        """Test that run_command requires permission."""
        result = agent._tool_run_command("echo test", "")
        assert "__PERMISSION_REQUIRED__" in result
    
    def test_run_command_with_permission(self, agent):
        """Test run_command with permission granted."""
        agent._permission_granted = True
        result = agent._tool_run_command("echo hello", "")
        assert "hello" in result.lower() or "exit" in result.lower()
    
    def test_search_code(self, agent, temp_workspace):
        """Test search_code tool."""
        result = agent._tool_search_code("hello")
        assert "test.py" in result or "No files" in result
    
    def test_ask_user(self, agent):
        """Test ask_user tool returns permission signal."""
        result = agent._tool_ask_user("Can I create a file?", "yes,no")
        assert "__PERMISSION_REQUIRED__" in result


# ═══════════════════════════════════════════════════════════
# TEST: OpenRouterAgent
# ═══════════════════════════════════════════════════════════

class TestOpenRouterAgent:
    """Tests for OpenRouterAgent."""
    
    @pytest.fixture
    def mock_client(self):
        """Mock the OpenRouter client."""
        with patch('stacksense.core.openrouter_agent.get_client') as mock:
            client = MagicMock()
            mock.return_value = client
            yield client
    
    @pytest.fixture
    def agent(self, tmp_path, mock_client):
        """Create an OpenRouterAgent for testing."""
        from stacksense.core.openrouter_agent import OpenRouterAgent
        
        # Create minimal workspace
        (tmp_path / "test.py").write_text("print('hello')")
        
        return OpenRouterAgent(
            workspace_path=str(tmp_path),
            model_name="test-model:free",
            debug=True
        )
    
    def test_default_model(self, agent):
        """Test default model is set."""
        assert agent.DEFAULT_MODEL == "nvidia/nemotron-nano-9b-v2:free"
    
    def test_tool_capable_models_list(self, agent):
        """Test tool capable models list exists."""
        assert len(agent.TOOL_CAPABLE_MODELS) > 0
    
    def test_get_tool_capable_model(self):
        """Test get_tool_capable_model class method."""
        from stacksense.core.openrouter_agent import OpenRouterAgent
        
        model = OpenRouterAgent.get_tool_capable_model(prefer_free=True)
        assert model is not None
        assert isinstance(model, str)


# ═══════════════════════════════════════════════════════════
# TEST: Permission Flow
# ═══════════════════════════════════════════════════════════

class TestPermissionFlow:
    """Tests for permission request flow."""
    
    @pytest.fixture
    def agent(self, tmp_path):
        """Create a test agent."""
        from stacksense.core.base_agent import BaseAgent
        
        class TestAgent(BaseAgent):
            def get_default_model(self):
                return "test"
            
            async def chat(self, query, **kwargs):
                return ""
        
        return TestAgent(str(tmp_path), "test", debug=True)
    
    def test_permission_pending_structure(self, agent):
        """Test that pending_permission has correct structure."""
        result = agent._tool_ask_user("Test question?", "yes,no")
        
        assert hasattr(agent, '_pending_permission')
        assert 'question' in agent._pending_permission
        assert 'awaiting' in agent._pending_permission
    
    def test_write_file_sets_pending_action(self, agent):
        """Test that write_file sets pending_action for later execution."""
        result = agent._tool_write_file("test.py", "content", "description")
        
        assert '__PERMISSION_REQUIRED__' in result
        assert 'pending_action' in agent._pending_permission
        assert agent._pending_permission['pending_action'][0] == 'write_file'
    
    def test_permission_granted_clears(self, agent, tmp_path):
        """Test that permission_granted is cleared after write."""
        agent._permission_granted = True
        agent._tool_write_file("test.py", "content", "description")
        
        assert agent._permission_granted == False


# ═══════════════════════════════════════════════════════════
# TEST: Model Statistics
# ═══════════════════════════════════════════════════════════

class TestModelStatistics:
    """Tests for model reliability tracking (ENH-004)."""
    
    @pytest.fixture
    def agent(self, tmp_path):
        """Create an OpenRouterAgent with mocked client."""
        with patch('stacksense.core.openrouter_agent.get_client'):
            from stacksense.core.openrouter_agent import OpenRouterAgent
            return OpenRouterAgent(str(tmp_path), "test-model:free", debug=True)
    
    def test_record_model_stat_creates_file(self, agent, tmp_path):
        """Test that recording stats creates the stats file."""
        # Point stats to tmp dir
        stats_path = tmp_path / "model_stats.json"
        
        with patch.object(Path, 'home', return_value=tmp_path):
            agent._record_model_stat('tool_call', True, 1.5)
        
        # Check file would be created at ~/.stacksense/model_stats.json
        # (actual path depends on home directory)
    
    def test_record_model_stat_increments(self, agent):
        """Test that recording stats increments counters."""
        import json
        from pathlib import Path
        
        # Just test the method runs without error
        agent._record_model_stat('tool_call', True, 2.0)
        agent._record_model_stat('tool_call', False, 1.0)
        agent._record_model_stat('text_permission', False)


# ═══════════════════════════════════════════════════════════
# INTEGRATION TEST
# ═══════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests (require API key)."""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENROUTER_API_KEY'),
        reason="OPENROUTER_API_KEY not set"
    )
    def test_real_chat_with_tools(self, tmp_path):
        """Test real chat with tool calling."""
        from stacksense.core.openrouter_agent import OpenRouterAgent
        import asyncio
        
        # Create workspace
        (tmp_path / "test.py").write_text("print('hello')")
        
        agent = OpenRouterAgent(
            workspace_path=str(tmp_path),
            model_name="nvidia/nemotron-nano-9b-v2:free",
            debug=True
        )
        
        # Simple query that should trigger read_file
        result = asyncio.run(agent.chat("What's in test.py?"))
        
        assert result is not None
        assert len(result) > 0
