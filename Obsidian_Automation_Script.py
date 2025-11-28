import os
import random
import datetime
import ollama

# --- CONFIGURATION ---
# ⚠️ USER: Update this path to your local Obsidian Vault
# Example: r"C:\Users\YourName\Documents\Obsidian Vault"
VAULT_PATH = r"/path/to/your/obsidian/vault"

# AI Configuration
MODEL_NAME = "llama3.2-vision" 
PRODUCTIVITY_THRESHOLD = 500  # Words written today to trigger 'Deep Work' mode

def get_vault_activity_stats():
    """
    Scans the vault to separate notes into recent (last 24h) and older files.
    Calculates the total word count of notes modified today to determine
    the complexity of the quiz.
    """
    recent_notes = []
    old_notes = []
    today_word_count = 0
    
    # Define 'recent' as modified within the last 24 hours
    limit_date = datetime.datetime.now() - datetime.timedelta(days=1)

    if not os.path.exists(VAULT_PATH):
        print(f"❌ Error: Vault path not found: {VAULT_PATH}")
        return [], [], 0

    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            # Skip the quiz files themselves to avoid recursion loops
            if file.endswith(".md") and "Daily Quiz" not in file:
                full_path = os.path.join(root, file)
                
                try:
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
                    
                    if mtime > limit_date:
                        recent_notes.append(full_path)
                        # Calculate words for the productivity score
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            today_word_count += len(content.split())
                    else:
                        old_notes.append(full_path)
                except OSError:
                    pass

    return recent_notes, old_notes, today_word_count

def check_weak_areas():
    """
    Scans the last 7 daily quiz files looking for the user-added tag #missed.
    Returns a summary string to feed into the AI context.
    """
    missed_counts = 0
    limit_date = datetime.datetime.now() - datetime.timedelta(days=7)
    
    for root, dirs, files in os.walk(VAULT_PATH):
        for file in files:
            if "Daily Quiz" in file and file.endswith(".md"):
                full_path = os.path.join(root, file)
                try:
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
                    if mtime > limit_date:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if "#missed" in f.read():
                                missed_counts += 1
                except:
                    continue
    
    if missed_counts > 0:
        return f"ATTENTION: The user marked {missed_counts} quizzes as containing errors or missed concepts this week. Focus on reinforcing weak areas."
    return "User performance has been clean recently."

def get_note_content(note_path):
    """Safely reads note content."""
    try:
        with open(note_path, "r", encoding="utf-8", errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {note_path}: {e}")
        return ""

def generate_session():
    print("Starting Exam Simulation Analysis...")
    recent_notes, old_notes, word_count = get_vault_activity_stats()
    
    # 1. Determine Difficulty
    if word_count > PRODUCTIVITY_THRESHOLD:
        print(f"High Volume ({word_count} words). Generaring 8 Exam Questions.")
        q_recent, q_old = 5, 3
    else:
        print(f"Low Volume ({word_count} words). Generating 5 Exam Questions.")
        q_recent, q_old = 3, 2

    # 2. Select Notes
    selected_notes = []
    # Weighted random selection
    if recent_notes: selected_notes.extend(random.sample(recent_notes, min(len(recent_notes), q_recent)))
    if old_notes: selected_notes.extend(random.sample(old_notes, min(len(old_notes), q_old)))

    if not selected_notes:
        print("No notes found to process.")
        return

    # 3. Build Context
    context_text = ""
    for note in selected_notes:
        text = get_note_content(note)
        # Limit text length to avoid context overflow on smaller GPUs
        clean_text = text[:1500].replace("\n", " ") 
        context_text += f"\n<source_note title='{os.path.basename(note)}'>\n{clean_text}\n</source_note>"

    # 4. The "Exam Mode" System Prompt
    system_instruction = """
    You are a professional Cybersecurity Certification Exam Creator.
    
    INSTRUCTIONS:
    1. Read the <source_note> content.
    2. Create a MULTIPLE CHOICE QUIZ (A, B, C, D).
    3. **CRITICAL:** Use the "Callout" format below. Do not use HTML tags like <details>.

    EXAMPLE OUTPUT FORMAT (Copy exactly):
    
    ### 🛡️ Question 1
    > [!QUESTION] **What flag is used in Nmap for a UDP scan?**
    > A) -sT
    > B) -sU
    > C) -sS
    > D) -Pn

    > [!SUCCESS]- 🔑 **Click to Reveal Answer**
    > **✅ Correct Answer:** B) -sU
    > **📝 Explanation:** The -sU flag specifically targets UDP ports.
    > **🔗 Source:** [[Nmap Scanning.md]]
    
    ---
    """

    print(f"Generating Exam Questions with Ollama ({MODEL_NAME})...")

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': f"Here is the study material:\n{context_text}\n\nGENERATE THE EXAM NOW."}
            ]
        )

        # Save Output
        quiz_content = response['message']['content']
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join(VAULT_PATH, f"Daily Quiz - {date_str}.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# 🎓 Daily Security Exam: {date_str}\n")
            f.write(f"**Sources:** {', '.join([os.path.basename(n) for n in selected_notes])}\n")
            f.write("---\n\n")
            f.write(quiz_content)

        print(f"✅ Success! Exam saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_session()