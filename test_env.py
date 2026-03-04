import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print environment variables (with partial masking for sensitive data)
def mask_string(s):
    if not s:
        return None
    return s[:8] + "..." + s[-4:] if len(s) > 12 else "***"

env_vars = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_ANON_KEY": mask_string(os.getenv("SUPABASE_ANON_KEY")),
    "OPENAI_API_KEY": mask_string(os.getenv("OPENAI_API_KEY")),
    "MODEL": os.getenv("MODEL")
}

print("Environment variables:")
for key, value in env_vars.items():
    print(f"{key}: {value}")
