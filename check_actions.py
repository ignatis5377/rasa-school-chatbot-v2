
from rasa_sdk.events import UserUttered, Restarted

class ActionHandleFallback(Action):
    def name(self) -> Text:
        return "action_handle_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Count consecutive fallbacks
        # Start with 1 (the current one)
        fallback_count = 1
        
        # Iterate backwards through events ignoring the immediate current state
        # We look for UserUttered events.
        # If the intent was nlu_fallback, we increment.
        # If the intent was something else (and not None), we stop counting.
        
        # Note: The *current* user message caused this action. Its intent is likely nlu_fallback.
        # We need to see if the *previous* user message was also nlu_fallback.
        
        print("DEBUG FALLBACK: Checking history for consecutive failures...")
        
        # We need to skip the *current* turn's user event because that's always nlu_fallback (which triggered this).
        # Actually, let's just count ALL consecutive nlu_fallbacks from the end.
        
        for event in reversed(tracker.events):
            if event.get("event") == "user":
                parse_data = event.get("parse_data", {})
                intent_name = parse_data.get("intent", {}).get("name")
                
                # If we just started iteration, this is the current message.
                # It *should* be nlu_fallback.
                
                if intent_name == "nlu_fallback":
                    # Determine if we should increment beyond the first one
                    # We can store matches in a list or just count
                    pass # logic below
                else:
                    # Found a valid intent! Stop counting.
                    break
        
        # Let's try a simpler approach since "parse_data" availability might vary depending on configuration.
        # We can also check the "metadata" if we tag it? No.
        
        # Alternative: We can trust the tracker.latest_message which is the CURRENT one.
        # Then we look at the one before that.
        
        count = 0
        found_valid = False
        
        for event in reversed(tracker.events):
            if event.get("event") == "user":
                intent = event.get("parse_data", {}).get("intent", {}).get("name")
                if intent == "nlu_fallback":
                    count += 1
                else:
                    found_valid = True
                    break
        
        print(f"DEBUG FALLBACK: Consecutive Count = {count}")
        
        if count < 3:
            dispatcher.utter_message(response="utter_please_repeat")
            return []
        else:
            dispatcher.utter_message(response="utter_default")
            return [Restarted()]
