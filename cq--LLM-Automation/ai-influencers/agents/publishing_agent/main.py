# main.py (project root)
import os
from dotenv import load_dotenv
load_dotenv()

from agents.publishing_agent import run_twitter, run_linkedin, run_medium, run_reddit, run_instagram
DRY_RUN = os.getenv("DRY_RUN", "True").lower() in ("1","true","yes")

def choose():
    print("\nCapQuant Publishing Controller")
    print("1) Run Twitter (X)")
    print("2) Run LinkedIn")
    print("3) Run Medium")
    print("4) Run Reddit")
    print("5) Run Instagram")
    print("6) Run all")
    print("0) Exit")
    ch = input("Choose (e.g. 1 or 1,3): ").strip()
    return ch

def run_choice(raw):
    picks = [p.strip() for p in raw.split(",") if p.strip().isdigit()]
    mapping = {
        "1": ("Twitter", run_twitter),
        "2": ("LinkedIn", run_linkedin),
        "3": ("Medium", run_medium),
        "4": ("Reddit", run_reddit),
        "5": ("Instagram", run_instagram)
    }
    if "6" in picks:
        picks = list(mapping.keys())
    for k in picks:
        name, func = mapping.get(k, (None, None))
        if not func:
            print(f"Invalid choice: {k}")
            continue
        print(f"\n--- Running {name} (DRY_RUN={DRY_RUN}) ---")
        try:
            func(DRY_RUN)
        except Exception as e:
            print(f"Error running {name}: {e}")

def main():
    print("CapQuant main controller. DRY_RUN =", DRY_RUN)
    while True:
        ch = choose()
        if ch == "0":
            print("Bye")
            break
        run_choice(ch)
        again = input("Run again? (y/n): ").strip().lower()
        if again != "y":
            break

if __name__ == "__main__":
    main()
