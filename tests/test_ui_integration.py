def test_metrics_panel_integration():
    """Test that key metrics panel correctly uses TCO model data."""
    # Create test scenario
    from tco_model.calculator import TCOCalculator
    from tco_model.models import ScenarioInput, VehicleType
    
    calculator = TCOCalculator()
    
    # Create test scenarios with proper vehicle types
    scenario1 = ScenarioInput(
        scenario_name="Test BET Scenario",
        vehicle={
            "name": "Test Electric",
            "type": VehicleType.BATTERY_ELECTRIC,
            "category": "rigid",
            "purchase_price": 500000,
            "annual_price_decrease_real": 0.02,
            "max_payload_tonnes": 12,
            "range_km": 300,
            "battery": {
                "capacity_kwh": 400,
                "usable_capacity_percentage": 0.9,
                "degradation_rate_annual": 0.02,
                "replacement_threshold": 0.7,
                "replacement_cost_factor": 0.8
            },
            "energy_consumption": {
                "base_rate": 1.5,
                "min_rate": 1.2,
                "max_rate": 1.8,
                "load_adjustment_factor": 0.3,
                "regenerative_braking_efficiency": 0.65,
                "regen_contribution_urban": 0.2
            },
            "charging": {
                "max_charging_power_kw": 150,
                "charging_efficiency": 0.9,
                "strategy": "overnight_depot"
            },
            "maintenance": {
                "cost_per_km": 0.15,
                "annual_fixed_min": 5000,
                "annual_fixed_max": 8000,
                "scheduled_maintenance_interval_km": 30000,
                "major_service_interval_km": 100000
            },
            "residual_value": {
                "year_5_range": [0.5, 0.6],
                "year_10_range": [0.2, 0.3],
                "year_15_range": [0.1, 0.15]
            }
        },
        operational={
            "annual_distance_km": 100000,
            "operating_days_per_year": 250,
            "is_urban_operation": False,
            "average_load_factor": 0.8
        },
        economic={
            "discount_rate_real": 0.07,
            "inflation_rate": 0.025,
            "analysis_period_years": 8,
            "carbon_tax_rate_aud_per_tonne": 30,
            "carbon_tax_annual_increase_rate": 0.05
        },
        financing={
            "method": "loan",
            "loan_term_years": 5,
            "loan_interest_rate": 0.05,
            "down_payment_percentage": 0.2
        }
    )
    
    scenario2 = ScenarioInput(
        scenario_name="Test Diesel Scenario",
        vehicle={
            "name": "Test Diesel",
            "type": VehicleType.DIESEL,
            "category": "rigid",
            "purchase_price": 300000,
            "annual_price_decrease_real": 0.01,
            "max_payload_tonnes": 12,
            "range_km": 600,
            "engine": {
                "power_kw": 300,
                "displacement_litres": 13,
                "euro_emission_standard": "Euro 6",
                "adblue_required": True,
                "adblue_consumption_percent_of_diesel": 0.05,
                "co2_per_liter": 2.68
            },
            "fuel_consumption": {
                "base_rate": 0.35,
                "min_rate": 0.3,
                "max_rate": 0.4,
                "load_adjustment_factor": 0.1
            },
            "maintenance": {
                "cost_per_km": 0.18,
                "annual_fixed_min": 6000,
                "annual_fixed_max": 10000,
                "scheduled_maintenance_interval_km": 20000,
                "major_service_interval_km": 80000
            },
            "residual_value": {
                "year_5_range": [0.4, 0.5],
                "year_10_range": [0.15, 0.25],
                "year_15_range": [0.05, 0.1]
            }
        },
        operational={
            "annual_distance_km": 100000,
            "operating_days_per_year": 250,
            "is_urban_operation": False,
            "average_load_factor": 0.8
        },
        economic={
            "discount_rate_real": 0.07,
            "inflation_rate": 0.025,
            "analysis_period_years": 8,
            "carbon_tax_rate_aud_per_tonne": 30,
            "carbon_tax_annual_increase_rate": 0.05
        },
        financing={
            "method": "loan",
            "loan_term_years": 5,
            "loan_interest_rate": 0.05,
            "down_payment_percentage": 0.2
        }
    )
    
    # Calculate results
    result1 = calculator.calculate(scenario1)
    result2 = calculator.calculate(scenario2)
    comparison = calculator.compare(result1, result2)
    
    results = {
        "vehicle_1": result1,
        "vehicle_2": result2
    }
    
    # Test integration by verifying the values used in payback information
    from ui.results.metrics import get_payback_information
    payback_info = get_payback_information(result1, result2, comparison)
    
    # Verify payback info matches investment analysis
    assert payback_info["has_payback"] == comparison.investment_analysis.has_payback
    if comparison.investment_analysis.payback_years:
        assert payback_info["years"] == comparison.investment_analysis.payback_years
    assert payback_info["roi"] == comparison.investment_analysis.roi or 0
    
    # Test component details extraction
    from ui.results.dashboard import get_component_details
    from tco_model.terminology import UI_COMPONENT_KEYS
    
    # Test each component
    for component in UI_COMPONENT_KEYS:
        details = get_component_details(results, component)
        
        # Verify structure
        assert "component" in details
        assert details["component"] == component
        assert "vehicle_1" in details
        assert "vehicle_2" in details
        assert "difference" in details
        
        # Verify values
        vehicle1_value = details["vehicle_1"]["value"]
        vehicle2_value = details["vehicle_2"]["value"]
        
        # Compare with TCO calculator's component value
        calculator_value1 = calculator.get_component_value(result1, component)
        calculator_value2 = calculator.get_component_value(result2, component)
        
        assert abs(vehicle1_value - calculator_value1) < 0.01
        assert abs(vehicle2_value - calculator_value2) < 0.01 