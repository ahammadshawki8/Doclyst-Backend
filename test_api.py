"""Test script to find working ERNIE/AI endpoints"""
from gradio_client import Client

# Test PaddleOCR app endpoints
print("Testing PaddleOCR app...")
try:
    client = Client("https://app-u613z0mda075e806.aistudio-app.com/")
    print("Available endpoints:")
    print(client.view_api())
except Exception as e:
    print(f"Error: {e}")
