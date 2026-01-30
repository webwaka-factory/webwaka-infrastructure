"""Unit tests for classification manager."""

import pytest
from src.classification.classification_manager import ClassificationManager
from src.models.classification import ClassificationLevel


@pytest.fixture
def manager():
    """Create classification manager instance."""
    return ClassificationManager()


@pytest.mark.asyncio
async def test_classify_data(manager):
    """Test data classification."""
    classification = await manager.classify_data(
        data_id="data-12345",
        classification_level=ClassificationLevel.IDENTITY,
        data_type="user_profile",
        sensitivity="high",
        pii_present=True
    )
    
    assert classification.id == "class-001"
    assert classification.data_id == "data-12345"
    assert classification.classification_level == ClassificationLevel.IDENTITY
    assert classification.pii_present is True


@pytest.mark.asyncio
async def test_get_data_classification(manager):
    """Test retrieving data classification."""
    await manager.classify_data(
        data_id="data-12345",
        classification_level=ClassificationLevel.IDENTITY,
        data_type="user_profile"
    )
    
    classification = manager.get_data_classification("data-12345")
    
    assert classification is not None
    assert classification.data_id == "data-12345"


@pytest.mark.asyncio
async def test_list_pii_data(manager):
    """Test listing data with PII."""
    await manager.classify_data(
        data_id="data-1",
        classification_level=ClassificationLevel.IDENTITY,
        data_type="user_profile",
        pii_present=True
    )
    
    await manager.classify_data(
        data_id="data-2",
        classification_level=ClassificationLevel.OPERATIONAL,
        data_type="system_log",
        pii_present=False
    )
    
    pii_data = manager.list_pii_data()
    assert len(pii_data) == 1
    assert pii_data[0].data_id == "data-1"


@pytest.mark.asyncio
async def test_list_classifications_by_level(manager):
    """Test listing classifications by level."""
    await manager.classify_data(
        data_id="data-1",
        classification_level=ClassificationLevel.IDENTITY,
        data_type="user_profile"
    )
    
    await manager.classify_data(
        data_id="data-2",
        classification_level=ClassificationLevel.TRANSACTIONAL,
        data_type="transaction"
    )
    
    identity_data = manager.list_classifications_by_level(ClassificationLevel.IDENTITY)
    assert len(identity_data) == 1
    assert identity_data[0].classification_level == ClassificationLevel.IDENTITY
