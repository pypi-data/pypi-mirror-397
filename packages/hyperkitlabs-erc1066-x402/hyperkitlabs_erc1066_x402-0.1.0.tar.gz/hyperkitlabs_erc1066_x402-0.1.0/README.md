# ERC-1066-x402 Python SDK

Python SDK for interacting with the ERC-1066-x402 gateway.

## Installation

```bash
pip install hyperkitlabs-erc1066-x402
```

## Usage

```python
from erc1066_x402 import ERC1066Client, Intent

client = ERC1066Client('https://gateway.example.com')

intent = Intent(
    sender='0x...',
    target='0x...',
    data='0x...',
    value='0',
    nonce='0',
    validAfter='0',
    validBefore='0',
    policyId='0x...'
)

result = client.validate_intent(intent, 1)
action = client.map_status_to_action(result.status)

if action == 'execute':
    client.execute_intent(intent, 1)
```

## API

### ERC1066Client

- `validate_intent(intent, chain_id)` - Validate an intent
- `execute_intent(intent, chain_id)` - Execute an intent
- `map_status_to_action(status)` - Map status code to action

