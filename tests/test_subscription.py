"""Tests for Subscription model."""
import dataclasses
import pytest
from buzzing.model.subscription import Subscription

@pytest.fixture
def subscription():
    """Create a test subscription."""
    return Subscription(
        user_id=123456789,
        username="test_user",
        bot_id=1,
        is_active=True
    )

def test_subscription_creation(subscription):
    """Test subscription creation."""
    assert subscription.user_id == 123456789
    assert subscription.username == "test_user"
    assert subscription.bot_id == 1
    assert subscription.is_active is True

def test_subscription_immutability(subscription):
    """Test that Subscription is immutable."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        subscription.is_active = False
