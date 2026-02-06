
import ast
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

file_path = "actions/actions.py"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse AST to find classes
    tree = ast.parse(content)
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    
    print("--- Found Classes ---")
    for c in classes:
        print(c)
        
    required = ["ActionSmartFaq", "ActionVerifyRole", "ActionHandleFallback", "ActionProvideStudyMaterial"]
    missing = [r for r in required if r not in classes]
    
    if missing:
        print(f"\nCRITICAL: Missing classes: {missing}")
    else:
        print("\nAll required classes present.")

except SyntaxError as e:
    print(f"SYNTAX ERROR in actions.py: {e}")
except Exception as e:
    print(f"Error: {e}")
