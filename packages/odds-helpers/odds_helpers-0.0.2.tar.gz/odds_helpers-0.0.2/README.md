### odds-helpers

## Functions

| Function | Parameters | Aliases | Description |
|----------|------------|---------|-------------|
| `moneyline_to_prob` | `ml`, `places=2` | `to_p`, `to_prob`, `ml_to_p`, `ml_to_prob` | Converts a moneyline to implied probability |
| `prob_to_moneyline` | `prob` | `to_ml`, `p_to_ml`, `prob_to_ml` | Converts a probability to moneyline format |
| `remove_vig` | `prob1`, `prob2` | `no_vig` | Removes the vig from two probabilities, returning fair odds |
| `total_juice` | `ml1`, `ml2` | `juice` | Calculates the total juice/vig from two moneylines |
| `payout` | `price`, `wager` | `profit` | Calculates the payout for a given price and wager amount |
| `base_to_risk` | `ml`, `base_amt` | — | Converts a base amount to risk amount based on moneyline |
| `ml_to_fractional` | `ml` | — | Converts moneyline to fractional odds |
| `get_ev` | `ml`, `est_prob`, `unit=1`, `verbose=True` | — | Calculates expected value given moneyline and estimated probability |
| `get_kelly` | `p`, `ml`, `verbose=True` | — | Calculates Kelly criterion bet fraction |