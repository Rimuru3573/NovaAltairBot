lines = open("bot.log", encoding="utf-8", errors="replace").read().splitlines()
for i, l in enumerate(lines):
    if "errors for UserOut" in l or "errors for UserIn" in l:
        print("LINE", i+1, "|", l.strip())
        print("\n".join(lines[i+1:i+14]))
        print("-" * 60)
