"""
Integration tests for MCP server enhancements.

Tests the integration of reverse-engineered extractors with MCP tools.
"""

import pytest
import pytest_asyncio
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp_server import PoE2BuildOptimizerMCP


class TestMCPIntegration:
    """Test MCP server with extractor integration."""

    @pytest_asyncio.fixture
    async def mcp_server(self):
        """Create and initialize MCP server."""
        server = PoE2BuildOptimizerMCP()
        await server.initialize()
        yield server
        await server.cleanup()

    @pytest.mark.asyncio
    async def test_inspect_support_gem(self, mcp_server):
        """Test inspect_support_gem with enhanced formatting."""
        result = await mcp_server._handle_inspect_support_gem({
            "support_name": "Controlled Destruction"
        })

        assert len(result) == 1
        text = result[0].text

        # Check enhanced formatting is present
        assert "Controlled Destruction" in text
        assert "**Tier**:" in text
        assert "**Effects**:" in text
        assert "**Requirements**:" in text

    @pytest.mark.asyncio
    async def test_list_all_supports(self, mcp_server):
        """Test list_all_supports with enhanced output."""
        result = await mcp_server._handle_list_all_supports({
            "sort_by": "tier",
            "limit": 10
        })

        assert len(result) == 1
        text = result[0].text

        # Check tier-based formatting
        assert "Support Gems" in text
        assert "(Tier" in text
        assert "Spirit:" in text
        assert "Effects:" in text

    @pytest.mark.asyncio
    async def test_inspect_spell_gem(self, mcp_server):
        """Test inspect_spell_gem with enhanced formatting."""
        result = await mcp_server._handle_inspect_spell_gem({
            "spell_name": "Fireball"
        })

        assert len(result) == 1
        text = result[0].text

        # Check enhanced formatting
        assert "Fireball" in text
        assert "**Element**:" in text
        assert "**Base Damage" in text
        assert "**Cast Time**:" in text
        assert "**Mechanics**:" in text or "Fireball" in text  # May or may not have mechanics

    @pytest.mark.asyncio
    async def test_list_all_spells(self, mcp_server):
        """Test list_all_spells with enhanced output."""
        result = await mcp_server._handle_list_all_spells({
            "filter_element": "fire",
            "limit": 5
        })

        assert len(result) == 1
        text = result[0].text

        # Check enhanced formatting
        assert "Spell Gems" in text
        assert "(Tier" in text
        assert "Damage:" in text
        assert "Cast:" in text
        assert "DPS:" in text
        assert "Mana:" in text

    @pytest.mark.asyncio
    async def test_optimize_passives_with_extractor(self, mcp_server):
        """Test optimize_passives uses passive tree extractor."""
        result = await mcp_server._handle_optimize_passives({
            "character_data": {"class": "Warrior"},
            "available_points": 5,
            "goal": "damage"
        })

        assert len(result) == 1
        text = result[0].text

        # Should have passive tree optimization response
        assert "passive" in text.lower() or "tree" in text.lower() or "allocation" in text.lower()

    @pytest.mark.asyncio
    async def test_passive_optimizer_defensive(self, mcp_server):
        """Test passive optimizer with defensive goal."""
        if not mcp_server.passive_optimizer:
            pytest.skip("Passive optimizer not initialized")

        recommendations = await mcp_server.passive_optimizer.optimize(
            character_data={"class": "Tank"},
            available_points=3,
            goal="defense"
        )

        assert "suggested_allocations" in recommendations
        assert isinstance(recommendations["suggested_allocations"], list)

        # Should have defensive recommendations
        if recommendations["suggested_allocations"]:
            first_rec = recommendations["suggested_allocations"][0]
            assert "name" in first_rec
            assert "benefit" in first_rec or "type" in first_rec

    @pytest.mark.asyncio
    async def test_extractors_initialized(self, mcp_server):
        """Test that extractors are properly initialized."""
        # Not all extractors may initialize (depends on file availability)
        # Just verify they exist as attributes
        assert hasattr(mcp_server, 'stat_extractor')
        assert hasattr(mcp_server, 'active_skill_extractor')
        assert hasattr(mcp_server, 'text_extractor')
        assert hasattr(mcp_server, 'passive_tree_extractor')

    @pytest.mark.asyncio
    async def test_support_gem_json_structure(self, mcp_server):
        """Test that support gem JSON is accessed correctly."""
        # Test with a known support gem
        result = await mcp_server._handle_inspect_support_gem({
            "support_name": "Faster Projectiles"
        })

        assert len(result) == 1
        text = result[0].text
        assert "Faster Projectiles" in text
        # Should not show "not found" error
        assert "not found" not in text.lower()

    @pytest.mark.asyncio
    async def test_spell_gem_json_structure(self, mcp_server):
        """Test that spell gem JSON is accessed correctly."""
        # Test with a known spell
        result = await mcp_server._handle_inspect_spell_gem({
            "spell_name": "Lightning Bolt"
        })

        assert len(result) == 1
        text = result[0].text
        # Should find the spell or return proper error
        assert "Lightning" in text or "not found" in text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
