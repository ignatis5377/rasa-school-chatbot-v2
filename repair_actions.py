
import os
import codecs

file_path = "actions/actions.py"

clean_fallback_code = """

class ActionHandleFallback(Action):
    def name(self) -> Text:
        return "action_handle_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        user_message = tracker.latest_message.get('text')
        
        # --- DYNAMIC SEARCH INTEGRATION ---
        if user_message and len(user_message) > 3:
            try:
                import requests
                # Search Posts
                url_posts = f"https://ignatislask.sites.sch.gr/?rest_route=/wp/v2/posts&search={user_message}&per_page=3"
                # Search Pages ensures we find 'Regulation' etc.
                url_pages = f"https://ignatislask.sites.sch.gr/?rest_route=/wp/v2/pages&search={user_message}&per_page=3"
                
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                
                posts = []
                try:
                    # Verify=False to avoid SSL errors on school network
                    r1 = requests.get(url_posts, headers=headers, timeout=3, verify=False)
                    if r1.status_code == 200: posts.extend(r1.json())
                except: pass
                
                try:
                    r2 = requests.get(url_pages, headers=headers, timeout=3, verify=False)
                    if r2.status_code == 200: posts.extend(r2.json())
                except: pass

                if posts:
                    message = "Δεν είμαι σίγουρος ότι κατάλαβα, αλλά βρήκα αυτά στο site:\\n\\n"
                    # Dedup by link
                    seen_links = set()
                    count = 0
                    for post in posts:
                        if count >= 3: break
                        link = post['link']
                        if link not in seen_links:
                            title = post['title']['rendered']
                            message += f"- [{title}]({link})\\n"
                            seen_links.add(link)
                            count += 1
                    
                    if count > 0:
                        message += "\\nΉταν αυτό που ψάχνατε;"
                        dispatcher.utter_message(text=message)
                        from rasa_sdk.events import UserUtteranceReverted
                        return [UserUtteranceReverted()]
                        
            except Exception as e:
                print(f"Fallback Search Error: {e}")

        dispatcher.utter_message(text="Συγνώμη, δεν κατάλαβα. Μπορείτε να το διατυπώσετε διαφορετικά;")
        return []
"""

# Read binary to safely handle the end
with open(file_path, "rb") as f:
    content_bytes = f.read()

# Convert to string (ignoring errors at the end where it's corrupt)
content_str = content_bytes.decode("utf-8", errors="ignore")

# Find where the corruption likely started.
# We know the last GOOD class was ActionUploadStudyMaterial.
# Or we can search for "class ActionHandleFallback" and cut before it.

marker = "class ActionHandleFallback"
idx = content_str.find(marker)

if idx != -1:
    # Cut before the marker
    valid_content = content_str[:idx]
else:
    # If marker not found (because it's garbled), search for the end of the previous class
    # "return [SlotSet(\"upload_file_path\", None), SlotSet(\"subject\", None), SlotSet(\"grade\", None)]"
    end_marker = 'return [SlotSet("upload_file_path", None), SlotSet("subject", None), SlotSet("grade", None)]'
    idx = content_str.find(end_marker)
    if idx != -1:
        # Include the marker line
        valid_content = content_str[:idx+len(end_marker)]
    else:
        print("Could not find cut-off point! Aborting safely.")
        exit(1)

# Write back valid content + new clean code
with open(file_path, "w", encoding="utf-8") as f:
    f.write(valid_content + clean_fallback_code)

print("Fixed actions.py!")
