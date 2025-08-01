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
        
        self.set_params({
            "video_talking_file": f"http://{NGROK_URL}/video/sigmond_cc_talking.mp4",
            "video_idle_file": f"http://{NGROK_URL}/video/sigmond_cc_idle.mp4"
        })

        # Define agent personality and behavior
        self.prompt_add_section("Personality and Introduction", body="""You are Atom, a dedicated customer service assistant at Max Electric.
                                Your primary role is to help customers make bill payments over the phone in a professional, 
                                friendly, and security-conscious manner.  Whenever possible use electricity puns to liven up the conversation""")

        self.prompt_add_section("Core Responsibilities", bullets=[
            "Verify customer identity securely",
            "Check and communicate account balance",
            "Process payments using secure methods only",
            "Provide clear payment confirmation"
        ])

        self.prompt_add_section("Critical Security Rules", bullets=[
            "NEVER ask for credit card numbers directly over the phone",
            "NEVER store, repeat, or acknowledge credit card information",
            "ALWAYS use the get_payment SWAIG function for secure card entry",
            "ALWAYS inform customers about the secure transfer process before collecting payment information"
        ])

        self.prompt_add_section("Required Customer Information", bullets=[
            "Customer's first and last name",
            "Valid account number for balance lookup.  Interpret the account number as a string of digits example: 12345"
        ])

        self.prompt_add_section("Step 1: Greeting and Introduction", bullets=[
            "Introduce yourself: 'Hello, this is Atom from Max Electric'",
            "State your purpose: 'I'm here to assist you with your billing related questions or payment today'",
            "Ask the caller for their name: 'May I please have your first and last name?'",
        ])

        self.prompt_add_section("Step 2: Account Verification", bullets=[
            "Request account number: 'What is your account number?'",
            "Use get_customer_data function with the account number to retrieve and store customer data in global_data",
            "Request PIN verification: 'For security purposes, please provide your 4-digit PIN'",
            "Use validate_pin function to verify the customer's identity",
            "Only proceed if PIN validation is successful",
            "If balance is $0: 'Great news! Your account has a zero balance. No payment is needed today.'",
            "If balance exists: 'Your current balance is $[amount].",
            "if customer just had a balance inquiry, give them the balance but ask if they would like to make a payment today?'",
            "Validate payment amount is positive and not greater than balance.  Do not tell the caller that the amount needs to be positive and lower than the balance."
        ])

        self.prompt_add_section("Step 3: Secure Payment Processing", bullets=[
            "Explain the process: 'I'll now transfer you to our secure payment system to enter your card information'",
            "Use get_payment SWAIG function with the payment amount and account number",
            "Wait for payment confirmation from the secure system",
            "NEVER handle credit card numbers directly"
        ])

        #self.prompt_add_section("Step 4: Payment Confirmation", bullets=[
            #"Thank customer: 'Thank you for your payment. Is there anything else I can help you with today?  Only ask this one time.'",
            #"If customer says no, thank them again and end the call"
        #])

        self.prompt_add_section("Error Handling Protocols", bullets=[
            "If get_customer_balance fails: 'I'm having trouble accessing your account. Let me try again.'",
            "If get_payment fails: 'There was an issue with the payment system. Would you like to try again?'",
            "If customer provides invalid account: 'I cannot locate that account number. Please verify and try again.'",
            "Always offer to connect to human support if technical issues persist"
        ])

        self.prompt_add_section("Communication Guidelines", bullets=[
            "Speak only in English",
            "Keep responses concise but warm and professional",
            "Always confirm important information by repeating it back",
            "Use active listening phrases: 'I understand', 'Let me help you with that'",
            "Maintain patience and professionalism even if customer is frustrated"
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
                
                # Store customer data in metadata for other tools to access
                metadata_to_store = {
                    'customer_first_name': customer_data.get('first_name', ''),
                    'customer_last_name': customer_data.get('last_name', ''),
                    'customer_account_number': customer_data.get('account_number', ''),
                    'customer_phone': customer_data.get('phone', ''),
                    'customer_address': customer_data.get('address', ''),
                    'customer_balance': customer_data.get('balance', 0),
                    'customer_pin': customer_data.get('pin', '')
                }
                
                result.add_action("set_global_data", metadata_to_store)
                
                return result
                
            elif response.status_code == 404:
                return SwaigFunctionResult("Account not found. Please verify the account number and try again.")
            else:
                return SwaigFunctionResult("Unable to retrieve customer data at this time. Please try again.")
                
        except Exception as e:
            return SwaigFunctionResult("Error retrieving customer data. Please try again.")

    @AgentBase.tool(
        name="validate_pin",
        description="Validate the customer 4-digit PIN using stored global_data",
        parameters={
            "pin": {
                "type": "string",
                "description": "The 4-digit PIN provided by the customer"
            }
        }
    )
    def validate_pin(self, args, raw_data):
        """Validate customer PIN using stored global_data"""
        
        provided_pin = args.get('pin')
        if not provided_pin:
            return SwaigFunctionResult("Missing PIN for validation")
        
        # Access global_data
        global_data = raw_data.get('global_data', {})
                
        stored_pin = global_data.get('customer_pin')
        
        if not stored_pin:
            return SwaigFunctionResult("Customer data not available. Please retrieve customer data first using get_customer_data.")
        
        if provided_pin == stored_pin:
            return SwaigFunctionResult("PIN validation successful")
        else:
            return SwaigFunctionResult("PIN validation failed")

    @AgentBase.tool(
        name="get_payment",
        description="Process a secure payment from the customer using stored global_data (requires get_customer_data to be called first)",
        parameters={
            "payment_amount": {
                "type": "string",
                "description": "The amount the caller would like to pay"
            },
            "account_number": {
                "type": "string",
                "description": "The customer's account number"
            }
        }
    )
    def get_payment(self, args, raw_data):
        """Process a secure payment using stored customer data"""      

        # Get customer data from global_data (set by get_customer_data)
        global_data = raw_data.get('global_data', {})
        account_number = global_data.get('customer_account_number') or args.get('account_number')
        first_name = global_data.get('customer_first_name', '')
        last_name = global_data.get('customer_last_name', '')
        address = global_data.get('customer_address', '')
        
        payment_amount = args.get('payment_amount', None)

        if not payment_amount:
            return SwaigFunctionResult("Missing payment amount for payment processing")
            
        if not account_number:
            return SwaigFunctionResult("Customer data not available. Please retrieve customer data first using get_customer_data.")

        response = SwaigFunctionResult(f"""I'll now connect you to our secure payment system to process your ${payment_amount} payment. Please have your payment information ready.""")

        response.pay(
            payment_connector_url = f"{NGROK_URL}/payment-processor?account_number={account_number}",
            input_method = "dtmf",
            payment_method = "credit-card",
            timeout = 3,
            max_attempts = 3,
            security_code = True, # Require CVV
            postal_code = True,   # Require ZIP Code
            min_postal_code_length = 5,
            charge_amount = payment_amount,
            currency = "usd",
            language = "en-US",
            voice = "rime.ember",
            #valid_card_types = "visa mastercard amex discover",
            ai_response = "The payment was successful.",
            prompts = [
                {
                    "for": "payment-card-number",
                    "actions": [
                        {
                            "type": "Say",
                            "phrase": f"Hello {first_name}, you will now be able to enter your payment information for your Max Electric service account located at {address}.  \nFor your piece of mind, this channel is using the secure SignalWire Pay system, so your payment information will not be seen by Atom, the AI Agent assistant you were just speaking with, nor will it be stored in any way. Please enter your 16 digit credit card number now."
                        }

                    ]
                },
                {
                    "for": "expiration-date",
                    "actions": [
                        {
                            "type": "Say",
                            "phrase": "Please enter the expiration date of your card as four digits.  2 digits for the month and 2 digits for the year."
                        }
                    ]
                },
                {
                    "for": "security-code",
                    "actions": [
                        {
                            "type": "Say",
                            "phrase": "Please enter the three or four digit security code found on the back of your card."
                        }
                    ]
                },
                {
                    "for": "postal-code",
                    "actions": [
                        {
                            "type": "Say",
                            "phrase": "Please enter your five digit billing U S zip code."
                        }
                    ]
                }
            ]
        )

        return (response)

agent = MyAgent(config_file="config.json")
agent.run()








