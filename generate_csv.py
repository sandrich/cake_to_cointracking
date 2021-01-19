import pandas as pd
import glob

pd.options.display.float_format = '{:.2f}'.format

path = r'./csv' # use your path
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

df = pd.concat(li, axis=0, ignore_index=True).sort_values('Date')

ct_df = pd.DataFrame(columns=['Type', 'Buy Amount',	'Buy Currency',	'Sell Amount', 'Sell Currency', 'Fee', 'Fee Currency', 'Exchange', 'Trade-Group', 'Comment', 'Date'])

def append_by_type(t, date, buy_amount=0, buy_cur="", sell_amount=0, sell_cur="", fee_amount=0, fee_cur=""):
    return ct_df.append({ 
        'Type': t,
        'Buy Amount': buy_amount,
        'Buy Currency': buy_cur,
        'Sell Amount': sell_amount,
        'Sell Currency': sell_cur,
        'Fee': fee_amount,
        'Fee Currency': fee_cur,
        'Date': date
    }, ignore_index=True)
for i, row in df.iterrows():
    if row['Operation'] == 'Signup bonus':
        ct_df = append_by_type('Airdrop', buy_amount=row['Amount'], buy_cur=row['Cryptocurrency'], date=row['Date'])
    
    if row['Operation'] == 'Deposit':
        ct_df = append_by_type('Deposit', buy_amount=row['Amount'], buy_cur=row['Cryptocurrency'], date=row['Date'])
    
    if row['Operation'] == 'Withdrawal':
        ct_df = append_by_type('Withdrawal', sell_amount=abs(row['Amount']), sell_cur=row['Cryptocurrency'], date=row['Date'])
    
    if row['Operation'] == 'Unstake fee':
        ct_df = append_by_type('Withdrawal', sell_amount=abs(row['Amount']), sell_cur=row['Cryptocurrency'], date=row['Date'])

    if row['Operation'] == 'Staking reward':
        ct_df = append_by_type('Reward / Bonus', buy_amount=row['Amount'], buy_cur=row['Cryptocurrency'], date=row['Date'])
    
    if 'Liquidity mining reward' in row['Operation']:
        ct_df = append_by_type('Reward / Bonus', buy_amount=row['Amount'], buy_cur=row['Cryptocurrency'], date=row['Date'])
    
    if row['Operation'] == 'Swapped in':
        # Find row with same date
        tmp = ct_df.loc[(ct_df['Date'] == row['Date']) & (ct_df['Type'] == 'Trade')]
        if len(tmp) == 0:
            ct_df = append_by_type('Trade', buy_amount=row['Amount'], buy_cur=row['Cryptocurrency'], date=row['Date'])
        else:
            ct_df.loc[(ct_df['Date'] == row['Date']) & (ct_df['Type'] == 'Trade'), ['Buy Amount', 'Buy Currency']] = [abs(row['Amount']), row['Cryptocurrency']]

    if row['Operation'] == 'Swapped out':
        # Find row with same date
        tmp = ct_df.loc[(ct_df['Date'] == row['Date']) & (ct_df['Type'] == 'Trade')]
        if len(tmp) == 0:
            ct_df = append_by_type('Trade', sell_amount=abs(row['Amount']), sell_cur=row['Cryptocurrency'], date=row['Date'])
        else:
            ct_df.loc[(ct_df['Date'] == row['Date']) & (ct_df['Type'] == 'Trade'), ['Sell Amount', 'Sell Currency']] = [abs(row['Amount']), row['Cryptocurrency']]


print(df)
print(ct_df)

ct_df['Date'] = pd.to_datetime(ct_df.Date)
ct_df['Date'] = ct_df['Date'].dt.strftime('%d.%m.%Y %H:%M:%S')

print(ct_df)

ct_df.to_csv('out.csv', index=False)