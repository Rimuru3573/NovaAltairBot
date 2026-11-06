import os
import sys

sys.path.insert(0, "src")

from novaaltairbot.config import Settings

print("settings loaded:", Settings().model_dump(exclude={"bot", "bot_api_key"}))

# Does pydantic-settings reject unknown env keys?
print("\nfields:", list(Settings.model_fields))
print("extra setting:", Settings.model_config.get("extra"))
