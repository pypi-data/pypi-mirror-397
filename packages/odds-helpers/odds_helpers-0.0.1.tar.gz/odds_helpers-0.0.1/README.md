### odds-helpers

## Functions

| Function | Parameters | Description |
|----------|------------|-------------|
| `moneyline_to_prob` | `ml`, `places=2` | Converts a moneyline to implied probability |
| `prob_to_moneyline` | `prob` | Converts a probability to moneyline format |
| `remove_vig` | `prob1`, `prob2` | Removes the vig from two probabilities, returning fair odds |
| `total_juice` | `ml1`, `ml2` | Calculates the total juice/vig from two moneylines |
| `payout` | `price`, `wager` | Calculates the payout for a given price and wager amount |
| `base_to_risk` | `ml`, `risk_amt` | Converts a base risk amount based on moneyline |- moneyline_to_prob
