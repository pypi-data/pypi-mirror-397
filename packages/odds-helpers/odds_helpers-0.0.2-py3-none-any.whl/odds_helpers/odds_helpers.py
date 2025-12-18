def moneyline_to_prob(ml,places=2):
    if ml < 0:
        prob = (-ml)/((-ml)+100)
    else:
        prob = 100/(ml + 100)
    prob = round(prob, places)
    return prob

to_p = to_prob = ml_to_p = ml_to_prob =  moneyline_to_prob
# tests = [-120,-300,-1000,-105,-180,200,100,105,450,3000]
# for test in tests:
#     print(test,moneyline_to_prob(test))
def prob_to_moneyline(prob):
    if(prob > 0.5):
        return round(-((prob/(1-prob))*100))
    else:
        return round((1-prob)/prob*100)

to_ml = p_to_ml = prob_to_ml = prob_to_moneyline
# tests = [.5,.6,.95,.4,.15,.25]
# for test in tests:
#     print(test,prob_to_moneyline(test))
def remove_vig(prob1, prob2):
    total = prob1+prob2
    prob1new = round(prob1/total,2)
    prob2new = round(prob2/total,2)
    return (prob1new, prob2new)

no_vig = remove_vig

def total_juice(ml1, ml2):
    p1 = moneyline_to_prob(ml1,4)
    p2 = moneyline_to_prob(ml2,4)
    return round(p1+p2-1,4)

juice = total_juice

def payout(price, wager):
    if price >= 100:
        return wager*(price/100)
    elif price <= -100:
        return wager/(abs(price)/100)
profit = payout

def base_to_risk(ml, base_amt):
    if ml > 0:
        return base_amt
    else:
        return abs(ml)/100*base_amt

def ml_to_fractional(ml):
    if ml >= 100:
        return ml/100
    elif ml <= -100:
        return 100/(ml*-1)
    else:
        raise ValueError('Incorrect Moneyline')
def get_ev(ml,est_prob,unit=1, verbose=True):
    book_prob = moneyline_to_prob(ml,places=3)
    win_pay = payout(ml,unit)
    loss_pay = -unit
    ev = (win_pay*est_prob) + (loss_pay*(1-est_prob)) 
    if verbose:
        print(f"Book Prob: {book_prob}, Our Estimated Prob: {est_prob}")
        print(f"EV: {round(ev,3)}")
    return ev
def get_kelly(p,ml, verbose=True): #p = probability of win, b is fractional odds given, q is probability of losing
    b = ml_to_fractional(ml)
    q = 1-p
    fraction = p - (q/b)
    if verbose:
        print(f"If est_prob is {p} and book_prob is {moneyline_to_prob(ml,places=3)} bet {round(fraction*100,2)}% of roll")
    return fraction