#%%
from os import close
from ok_finda import help
print(help())

#%%
from ok_finda import ff_reg
code_name={
        "600100.SH": "同方股份",
        "600626.SH": "申达股份",
        "000630.SZ": "铜陵有色",
        "000850.SZ": "华茂股份",
        "600368.SH": "五洲交通",
        "603766.SH": "隆鑫通用",
        "600105.SH": "永鼎股份",
        "600603.SH": "广汇物流",
        "002344.SZ": "海宁皮城",
        "000407.SZ": "胜利股份",
        "000883.SZ": "湖北能源"
        }
df = ff_reg(codes=code_name, start_date='2024-10-01', end_date='2025-10-31', mode=5)
print(df)
# outfile = "/FFReg_2025.csv"
# df.to_csv(outfile,index=False)

#%%


# %%
