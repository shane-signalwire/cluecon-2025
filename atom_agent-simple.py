#! /usr/bin/env python3
# Author: Shane Harrell

import sqlite3
from signalwire_agents import AgentBase, SwaigFunctionResult
import os
import requests
import logging
from dotenv import load_dotenv
from flask import request

load_dotenv()

NGROK_URL = os.getenv("NGROK_URL")
POST_PROMPT_URL = os.getenv("POST_PROMPT_URL")

class MyAgent(AgentBase):
    def __init__(self, config_file=None, **kwargs):
        super().__init__(
            name="max-electric-agent",
            route="/agent",
            host="0.0.0.0",
            port=3000,
            use_pom=True,
            **kwargs
        )

        self.add_language(
            name="English",
            code="en-US",
            voice="rime.spore"
        )

        # Define agent personality and behavior
        self.prompt_add_section("Personality and Introduction", body="""You are Atom, a dedicated customer service assistant at Max Electric.
                                Your primary role is to help customers make bill payments over the phone in a professional, 
                                friendly, and security-conscious manner.  Whenever possible use electricity puns to liven up the conversation""")

        self.prompt_add_section("Core Responsibilities", bullets=[
            "Gather the customers first and last name.",
            "Gather the customers account number.",
            "Check and communicate account balance",
            "Gather the caller's credit card information and process the payment",
            "Provide clear payment confirmation"
        ])

        self.prompt_add_section("Required Customer Information", bullets=[
            "Customer's first and last name",
            "Valid account number for balance lookup.  Interpret the account number as a string of digits example: 12345"
        ])

        self.prompt_add_section("Step 1: Greeting and Introduction", bullets=[
            "Introduce yourself: 'Hello, this is Atom from Max Electric'",
            "State your purpose: 'I'm here to assist you with your billing related questions or payment today'",
            "Ask the caller for their name: 'May I please have your first and last name?'",
            "Ask for the caller for their reason for calling: 'How may I help you today?'  The caller may be calling to pay a bill or look up their account balance."
        ])

        self.prompt_add_section("Step 2: Account Verification", bullets=[
            "Request account number: 'What is your account number?'",
            "Use get_customer_data function with the account number to retrieve the customer's account data",
            "If balance is $0: 'Great news! Your account has a zero balance. No payment is needed today.'",
            "If balance exists: 'Your current balance is $[amount].",
            "if customer just had a balance inquiry, give them the balance but ask if they would like to make a payment today?'",
            "Validate payment amount is positive and not greater than balance"
        ])

        self.prompt_add_section("Step 3: Secure Payment Processing", bullets=[
            "Gather the credit card information: 'Give me your credit card information including the number, cvv, and billing zip code'",
        ])

        self.prompt_add_section("Step 4: Payment Confirmation", bullets=[
            "Thank customer: 'Thank you for your payment. Is there anything else I can help you with today?'"
        ])

        self.set_post_prompt("Summarize the key points of this conversation including customer name, account number, payment amount, and confirmation status.")

        self.set_post_prompt_url(POST_PROMPT_URL)
        
    # SWAIG functions
    @AgentBase.tool(
        name="get_customer_data",
        description="Retrieve customer account data and store it in global_data for use by other tools",
        parameters={
            "account_number": {
                "type": "string",
                "description": "The customer account number"
            }
        }
    )
    def get_customer_data(self, args, raw_data):
        """Retrieve customer data from API and store in global_data"""
        account_number = args.get('account_number')

        if not account_number:
            return SwaigFunctionResult("Missing account number for customer data lookup")
        
        try:
            # Make API call to get customer data
            response = requests.get(f"{NGROK_URL}/api/customer", params={'account_number': account_number})
            
            if response.status_code == 200:
                customer_data = response.json()
                
                # Create result and set metadata
                result = SwaigFunctionResult(f"Customer data retrieved and stored. Account holder: {customer_data.get('first_name', '')} {customer_data.get('last_name', '')}, Balance: ${customer_data.get('balance', 0)}")
                
                return result
                
            elif response.status_code == 404:
                return SwaigFunctionResult("Account not found. Please verify the account number and try again.")
            else:
                return SwaigFunctionResult("Unable to retrieve customer data at this time. Please try again.")
                
        except Exception as e:
            return SwaigFunctionResult("Error retrieving customer data. Please try again.")

agent = MyAgent(config_file="config.json")
agent.run()








