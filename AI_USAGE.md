# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- Tool and version (e.g. ChatGPT GPT-5, Claude, GitHub Copilot): Claude

## Conversation links

- Link 1: https://claude.ai/share/06adb52a-68f3-453a-b60d-47e38c978769

## What I used them for

- e.g. explaining argparse, debugging the date validation, generating test data
for starting and figuring out if something is wrong with my code

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| validator.py | _parse_dt helper and structure of validate_row | Claude suggested a reusable strict datetime helper, ordered early returns in validate_row, and flagged edge cases (non-ASCII characters, unpadded dates, whitespace-only prices, and nan) |
| query.py | whole file |Claude suggested the validate-filter-sort-limit pipeline, flagged boolean and post-sort limit edge cases, and recommended reusing the datetime helper from validator.py.|
| csv_loader.py | parse_files | Claude gave advice: detect blank/comment lines before csv.reader, keep the duplicate set across files and add only valid rows, use the base file name.|
| flight_parser.py | main, logging | Claude advised only: remove and close the logging handler in try/finally, exit codes 1 and 2. I wrote the code. |

## Key prompts

1. Copy pasting the task information and asking help for starting.
2. Sending the starter files and asking for an order to start.
3. Asking for a review for query.py.

## What I changed or verified myself?
i wrote the code by using claude's advices. 
