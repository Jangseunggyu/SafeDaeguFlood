import pandas as pd
df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\국토교통부_저층주거 침수피해 시각화_20221201.csv",encoding='euc-kr', sep=None, engine='python')
df.head()
df['시도명'].unique()


df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\행정안전부_인명피해 우려지역 현황_20240731.csv",encoding='euc-kr', sep=None, engine='python')
df.head()
df.loc[df['시도'] == '대구광역시']


df = pd.read_csv("C:\\Users\\USER\\Desktop\cvs\\인천광역시 남동구_침수위험지역현황_20240729.csv",encoding='euc-kr', sep=None, engine='python')

df.head()


df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\대구광역시_소방 긴급구조 기상정보.csv",encoding='euc-kr', sep=None, engine='python')
df[df['제목'].str.contains("호우",na=False)]

[df['제목'] == '호우주의보 발표']

df['발표일시'].sort_values(ascending=False)



df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시_서구_하수시설 정비 계획_20240718.csv",encoding='euc-kr', sep=None, engine='python')
df.info()
df.head()

df = pd.read_csv("C:\\Users\\USER\\Desktop\\cvs\\대구광역시 북구_소하천_20240725.csv",encoding='949', sep=None, engine='python')
df
df.head()
df['종점위치'].unique()

df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시 달성군_배수펌프장_20240829.csv",encoding='949', sep=None, engine='python')
df.head()
df.loc[df['설치연도']=='1986']

df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시_빗물펌프장 현황_20250409.csv",encoding='949', sep=None, engine='python')

df = pd.read_csv("C:\\Users\\USER\\Desktop\대구\\대구광역시_달성군_재해위험지구_20200702_1593688929259_2221.csv",encoding='euc-kr', sep=None, engine='python')

df = pd.read_csv("C:\\Users\\USER\\Desktop\\대구\\대구광역시_수성구_재해위험지구_20200709_1594518868929_455.csv",encoding='euc-kr', sep=None, engine='python')
