import os
import re
import sys

aws_key_pattern = re.compile(r'AKIA[0-9A-Z]{16}')
found_secrets = False

for filename in os.listdir('.'):
    if filename.endswith('.tf') or filename.endswith('.json'):
        with open(filename, 'r') as file:
            content = file.read()
            
            if aws_key_pattern.search(content):
                print(f" CRITICAL: AWS Access Key exposed in {filename}!")
                found_secrets = True

if found_secrets:
    print("❌ Pipeline blocked. Remove the secrets before merging.")
    sys.exit(1)
else:
    print(" No secrets found. Code is secure.")
    sys.exit(0)