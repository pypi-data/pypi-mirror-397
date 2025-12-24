"""
PySI - Simple Code Reference
Usage:
    from pysi import help, smenu, scode
"""

from .snippets import SNIPPETS, CATS

def help():
    """Show all snippets"""
    print("\n=== PYSI SNIPPETS ===\n")
    for cat in CATS:
        items = [n for n, s in SNIPPETS.items() if s["cat"] == cat]
        print(f"{cat}: {', '.join(items)}")
    print("\nUse: scode('name') to get code")

def smenu():
    """Show menu by category"""
    print("\n=== MENU ===\n")
    for cat in CATS:
        print(f"[{cat}]")
        for name, s in SNIPPETS.items():
            if s["cat"] == cat:
                print(f"  - {name}")
        print()

def scode(name):
    """Get code snippet"""
    if name not in SNIPPETS:
        print(f"Not found: {name}")
        print("Available:", ", ".join(sorted(SNIPPETS.keys())))
        return
    
    s = SNIPPETS[name]
    code = ""
    
    if s["imports"]:
        code += s["imports"] + "\n\n"
    code += s["code"]
    
    print(code)

def search(kw):
    """Search snippets"""
    kw = kw.lower()
    found = [n for n in SNIPPETS if kw in n.lower()]
    if found:
        print("Found:", ", ".join(found))
    else:
        print("Nothing found")

def cat(name):
    """Show all snippets in a category"""
    for n, s in SNIPPETS.items():
        if s["cat"].lower() == name.lower():
            print(f"\n--- {n} ---")
            if s["imports"]:
                print(s["imports"])
                print()
            print(s["code"])

__all__ = ['help', 'smenu', 'scode', 'search', 'cat']
