import asyncio
from rasa.core.agent import Agent

async def test_nlu():
    print("Loading model...")
    # Load the latest model from 'models' directory
    try:
        agent = Agent.load("models")
        print("Model loaded.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    messages = ["διαβασμα", "θελω υλικο για διαβασμα", "ανεβασμα"]
    
    for msg in messages:
        print(f"\n--- Testing: '{msg}' ---")
        result = await agent.parse_message(msg)
        intent = result.get('intent', {}).get('name')
        conf = result.get('intent', {}).get('confidence')
        print(f"Predicted Intent: {intent} (Confidence: {conf:.4f})")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_nlu())
