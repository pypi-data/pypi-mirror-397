def moneyline_to_prob(ml,places=2):
    if ml < 0:
        prob = (-ml)/((-ml)+100)
    else:
        prob = 100/(ml + 100)
    prob = round(prob, places)
    return prob
# tests = [-120,-300,-1000,-105,-180,200,100,105,450,3000]
# for test in tests:
#     print(test,moneyline_to_prob(test))
def prob_to_moneyline(prob):
    if(prob > 0.5):
        return round(-((prob/(1-prob))*100))
    else:
        return round((1-prob)/prob*100)
# tests = [.5,.6,.95,.4,.15,.25]
# for test in tests:
#     print(test,prob_to_moneyline(test))
def remove_vig(prob1, prob2):
    total = prob1+prob2
    prob1new = round(prob1/total,2)
    prob2new = round(prob2/total,2)
    return (prob1new, prob2new)

def total_juice(ml1, ml2):
    p1 = moneyline_to_prob(ml1,4)
    p2 = moneyline_to_prob(ml2,4)
    return round(p1+p2-1,4)

def payout(price, wager):
    if price >= 100:
        return wager*(price/100)
    elif price <= -100:
        return wager/(abs(price)/100)
def base_to_risk(ml, risk_amt):
    if ml > 0:
        return risk_amt
    else:
        return risk_amt/(abs(ml)/100)
