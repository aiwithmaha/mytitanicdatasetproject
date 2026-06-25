passengers=2224
survivors=710
def survival_rate(total,saved):
    return saved/total*100
rate=survival_rate(passengers,survivors)
print('Titanic survival rate:',rate,'%')
