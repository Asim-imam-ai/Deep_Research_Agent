"""CLI: start and resume the main research graph using a single in-process checkpointer."""
import argparse
from research_assistant.services.research_service import start_research, resume_research


def main():
    parser = argparse.ArgumentParser(description='Run human-approved research')
    parser.add_argument('topic')
    parser.add_argument('--analysts', type=int, default=3)
    parser.add_argument('--turns', type=int, default=2)
    args = parser.parse_args()
    thread_id, state = start_research(args.topic, args.analysts, args.turns)
    while '__interrupt__' in state:
        print('Thread:', thread_id)
        for item in state['__interrupt__']:
            print('Approval needed:', item.value)
        response = input('Reply approve or provide correction feedback: ').strip() or 'approve'
        state = resume_research(thread_id, response)
    print(state['final_report'])

if __name__ == '__main__':
    main()
