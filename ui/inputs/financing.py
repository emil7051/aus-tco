"""
Financing Input Module

This module renders the UI components for financing parameter inputs,
handling loan terms, interest rates, and down payment percentages.
"""

import streamlit as st
from typing import Dict, Any, Optional

from tco_model.models import FinancingMethod
from utils.helpers import (
    get_safe_state_value, 
    set_safe_state_value, 
    format_currency
)


# Constants for state keys
STATE_FINANCING_METHOD = "method"
STATE_LOAN_TERM = "loan_term_years"
STATE_LOAN_INTEREST = "loan_interest_rate"
STATE_DOWN_PAYMENT = "down_payment_percentage"


def render_financing_inputs(vehicle_number: int) -> None:
    """
    Render the UI components for financing parameters.
    
    This function renders input fields for financing parameters such as
    loan term, interest rate, and down payment percentage.
    
    Args:
        vehicle_number: The vehicle number (1 or 2)
    """
    state_prefix = f"vehicle_{vehicle_number}_input"
    
    with st.expander("Financing Options", expanded=True):
        # Financing method
        financing_method = st.selectbox(
            "Financing Method",
            options=[fm.value for fm in FinancingMethod],
            index=0 if get_safe_state_value(f"{state_prefix}.financing.{STATE_FINANCING_METHOD}", 
                                         FinancingMethod.LOAN.value) == FinancingMethod.LOAN.value else 1,
            key=f"{state_prefix}.financing.{STATE_FINANCING_METHOD}_input",
            help="Method of financing the vehicle purchase"
        )
        set_safe_state_value(f"{state_prefix}.financing.{STATE_FINANCING_METHOD}", financing_method)
        
        # Conditional financing parameters
        if financing_method == FinancingMethod.LOAN.value:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                loan_term = st.slider(
                    "Loan Term (years)",
                    min_value=1,
                    max_value=10,
                    value=int(get_safe_state_value(f"{state_prefix}.financing.{STATE_LOAN_TERM}", 5)),
                    key=f"{state_prefix}.financing.{STATE_LOAN_TERM}_input",
                    help="Length of the loan in years"
                )
                set_safe_state_value(f"{state_prefix}.financing.{STATE_LOAN_TERM}", loan_term)
            
            with col2:
                interest_rate = st.number_input(
                    "Interest Rate (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=float(get_safe_state_value(f"{state_prefix}.financing.{STATE_LOAN_INTEREST}", 0.05)) * 100,
                    format="%.1f",
                    key=f"{state_prefix}.financing.{STATE_LOAN_INTEREST}_input",
                    help="Annual interest rate on the loan"
                )
                set_safe_state_value(f"{state_prefix}.financing.{STATE_LOAN_INTEREST}", interest_rate / 100.0)
            
            with col3:
                down_payment = st.number_input(
                    "Down Payment (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(get_safe_state_value(f"{state_prefix}.financing.{STATE_DOWN_PAYMENT}", 0.2)) * 100,
                    format="%.1f",
                    key=f"{state_prefix}.financing.{STATE_DOWN_PAYMENT}_input",
                    help="Percentage of purchase price paid as down payment"
                )
                set_safe_state_value(f"{state_prefix}.financing.{STATE_DOWN_PAYMENT}", down_payment / 100.0)
            
            # Calculate loan metrics based on purchase price
            purchase_price = get_safe_state_value(f"{state_prefix}.vehicle.purchase_price", 400000.0)
            
            # Display a warning if the purchase price is too high
            if purchase_price > 1000000:
                st.warning("Purchase price is very high. Please verify this value is correct.")
            
            # Calculate loan details
            loan_amount = purchase_price * (1 - down_payment/100)
            
            # Handle edge cases to prevent calculation errors
            if interest_rate <= 0 or loan_term <= 0 or loan_amount <= 0:
                st.error("Please ensure interest rate, loan term, and loan amount are all greater than zero.")
            else:
                # Calculate monthly payment using the formula: P × r × (1 + r)ⁿ ÷ ((1 + r)ⁿ - 1)
                monthly_interest_rate = interest_rate/100/12
                num_payments = loan_term * 12
                
                try:
                    monthly_payment = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments / ((1 + monthly_interest_rate) ** num_payments - 1)
                    annual_payment = monthly_payment * 12
                    total_payments = monthly_payment * num_payments
                    total_interest = total_payments - loan_amount
                    
                    # Display loan summary
                    st.subheader("Loan Summary")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Loan Amount", format_currency(loan_amount))
                        st.metric("Monthly Payment", format_currency(monthly_payment))
                        st.metric("Annual Payment", format_currency(annual_payment))
                    
                    with col2:
                        st.metric("Total Interest", format_currency(total_interest))
                        st.metric("Total Payments", format_currency(total_payments))
                        st.metric("Total Cost", format_currency(total_payments + purchase_price * down_payment/100))
                    
                    # Show loan amortization table
                    if st.checkbox("Show Loan Amortization Schedule", False):
                        st.subheader("Amortization Schedule")
                        
                        # Create a table with key loan amortization data
                        amortization_data = []
                        remaining_balance = loan_amount
                        
                        for year in range(1, loan_term + 1):
                            year_interest = 0
                            year_principal = 0
                            
                            for month in range(1, 13):
                                if remaining_balance <= 0:
                                    break
                                
                                month_interest = remaining_balance * monthly_interest_rate
                                year_interest += month_interest
                                
                                if month_interest >= monthly_payment:
                                    # Edge case: interest exceeds payment
                                    month_principal = 0
                                else:
                                    month_principal = monthly_payment - month_interest
                                
                                if month_principal > remaining_balance:
                                    month_principal = remaining_balance
                                
                                year_principal += month_principal
                                remaining_balance -= month_principal
                            
                            amortization_data.append({
                                "Year": year,
                                "Interest Paid": format_currency(year_interest),
                                "Principal Paid": format_currency(year_principal),
                                "Remaining Balance": format_currency(remaining_balance)
                            })
                        
                        # Display as a table
                        st.table(amortization_data)
                
                except (ValueError, ZeroDivisionError, OverflowError) as e:
                    st.error(f"Error calculating loan terms: {str(e)}")
        
        else:
            # Cash purchase
            purchase_price = get_safe_state_value(f"{state_prefix}.vehicle.purchase_price", 400000.0)
            
            st.info("Cash purchase: Full purchase price paid upfront with no financing costs.")
            
            # Display simple cash purchase summary
            st.subheader("Cash Purchase Summary")
            st.metric("Purchase Price", format_currency(purchase_price))
            st.metric("Financing Cost", "$0")
            st.metric("Total Cost", format_currency(purchase_price)) 