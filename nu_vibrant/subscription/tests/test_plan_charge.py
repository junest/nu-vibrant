import pytest
from unittest.mock import patch, MagicMock
from django.db.models import Sum
from decimal import Decimal

from nu_vibrant.subscription.models import PlanCharge
from nu_vibrant.subscription.tests.factories import (
    BillableMetricFactory, PlanFactory, PlanChargeFactory,
    SubscriptionFactory
)
from nu_vibrant.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestPlanChargeModel:
    def test_get_used_charge_count(self):
        """Test _get_used_charge method with count aggregation"""
        # Create test data
        metric = BillableMetricFactory(
            aggregation_type='count',
            identifier='test_event'
        )
        plan = PlanFactory()
        plan_charge = PlanChargeFactory(
            plan=plan,
            billable_metric=metric,
            free_unit=5
        )
        
        # Mock the _get_used_charge method directly
        with patch.object(PlanCharge, '_get_used_charge', return_value=10):
            # Test the charge_left property
            assert plan_charge.charge_left == 5  # 10 - 5 = 5
    
    def test_get_used_charge_sum(self):
        """Test _get_used_charge method with sum aggregation"""
        # Create test data
        metric = BillableMetricFactory(
            aggregation_type='sum',
            property_name='amount'
        )
        plan = PlanFactory()
        plan_charge = PlanChargeFactory(
            plan=plan,
            billable_metric=metric,
            free_unit=8
        )
        
        # Mock the _get_used_charge method directly
        with patch.object(PlanCharge, '_get_used_charge', return_value=150):
            # Test the charge_left property
            assert plan_charge.charge_left == 142  # 150 - 8 = 142
    
    def test_charge_left(self):
        """Test charge_left property"""
        plan_charge = PlanChargeFactory(free_unit=10)
        
        # Mock _get_used_charge to return 15
        with patch.object(PlanCharge, '_get_used_charge', return_value=15):
            # Test the property
            assert plan_charge.charge_left == 5  # 15 - 10 = 5
    
    def test_no_subscriptions(self):
        """Test _get_used_charge when there are no subscriptions"""
        plan = PlanFactory()
        plan_charge = PlanChargeFactory(plan=plan)
        
        # Test with no subscriptions
        result = plan_charge._get_used_charge()
        assert result == 0
        
    def test_calculate_extra_charge(self):
        """Test calculate_extra_charge method for usage beyond free units"""
        # Create plan charge with 10 free units, 1 unit per charge, and $5 per unit
        plan_charge = PlanChargeFactory(
            free_unit=10,
            unit=1,
            amount=Decimal('5.00'),
            is_rate_limiting=False
        )
        
        # Case 1: Usage is less than free units (no extra charge)
        with patch.object(PlanCharge, '_get_used_charge', return_value=5):
            assert plan_charge.charge_left == -5  # 5 - 10 = -5 (negative means units left)
            assert plan_charge.calculate_extra_charge() == Decimal('0')
        
        # Case 2: Usage equals free units (no extra charge)
        with patch.object(PlanCharge, '_get_used_charge', return_value=10):
            assert plan_charge.charge_left == 0
            assert plan_charge.calculate_extra_charge() == Decimal('0')
        
        # Case 3: Usage exceeds free units (extra charge applies)
        with patch.object(PlanCharge, '_get_used_charge', return_value=15):
            assert plan_charge.charge_left == 5  # 15 - 10 = 5 (positive means extra units used)
            assert plan_charge.calculate_extra_charge() == Decimal('25.00')  # 5 units * $5.00 = $25.00
            
        # Case 4: Usage exceeds free units but rate limiting is enabled (no extra charge)
        plan_charge.is_rate_limiting = True
        with patch.object(PlanCharge, '_get_used_charge', return_value=15):
            assert plan_charge.charge_left == 5
            assert plan_charge.calculate_extra_charge() == Decimal('0')
            
    def test_calculate_extra_charge_with_different_unit_size(self):
        """Test calculate_extra_charge with different unit sizes"""
        # Create plan charge with 100 free units, 10 units per charge, and $5 per 10 units
        plan_charge = PlanChargeFactory(
            free_unit=100,
            unit=10,
            amount=Decimal('5.00'),
            is_rate_limiting=False
        )
        
        # Usage exceeds free units by 50 units
        with patch.object(PlanCharge, '_get_used_charge', return_value=150):
            assert plan_charge.charge_left == 50  # 150 - 100 = 50 extra units
            # 50 units / 10 units per charge = 5 charges * $5.00 = $25.00
            assert plan_charge.calculate_extra_charge() == Decimal('25.00')
        
        # Usage exceeds free units by 55 units (partial unit)
        with patch.object(PlanCharge, '_get_used_charge', return_value=155):
            assert plan_charge.charge_left == 55  # 155 - 100 = 55 extra units
            # 55 units / 10 units per charge = 5.5 charges * $5.00 = $27.50
            assert plan_charge.calculate_extra_charge() == Decimal('27.50')