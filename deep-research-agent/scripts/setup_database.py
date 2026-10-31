"""Initialize application schema and LangGraph checkpoint schema."""
import subprocess
import sys
from research_assistant.infrastructure.checkpoint.postgres import setup_checkpointer

def main():
    subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], check=True)
    setup_checkpointer()
    print('Application migrations and LangGraph checkpoint setup completed.')

if __name__ == '__main__':
    main()
