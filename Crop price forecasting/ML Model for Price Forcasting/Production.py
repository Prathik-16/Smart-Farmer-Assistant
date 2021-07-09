import warnings
import itertools
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

#Pre-Procession
pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore", category=DeprecationWarning)
daily_Data= pd.read_excel("Agmarknet_Price_Report.xlsx")
df=daily_Data.copy()
df=df.rename(index=str, columns={"Sl no.": "Sl_no", "Min Price (Rs./Quintal)": "Min_Price","Price Date":"Price_Date","Modal Price (Rs./Quintal)":"Modal_Price"})
df.Price_Date = pd.to_datetime(df.Price_Date, errors='coerce')
df=df.sort_values(by='Price_Date')
df.drop_duplicates('Price_Date', inplace = True)
df.to_csv("File.csv", sep=',')


#Modal Preparation
plt.style.use('fivethirtyeight')
fields = ['Modal_Price', 'Price_Date']
df= pd.read_csv("File.csv",skipinitialspace=True, usecols=fields)
df.Price_Date = pd.to_datetime(df.Price_Date, errors='coerce')
df=df.set_index('Price_Date')
data = df.copy()
y = data
y = y['Modal_Price'].resample('MS').mean()
# The term bfill means that we use the value before filling in missing values
y = y.fillna(y.bfill())
print(y)
y.plot(figsize=(15, 6))
# Define the p, d and q parameters to take any value between 0 and 2
p = d = q = range(0, 2)
# Generate all different combinations of p, q and q triplets
pdq = list(itertools.product(p, d, q))
# Generate all different combinations of seasonal p, q and q triplets
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))
warnings.filterwarnings("ignore") # specify to ignore warning messages
for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(y,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)

            results = mod.fit()

            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

#Data Pre-Processing
from datetime import date
from dateutil.relativedelta import relativedelta
today = date.today()
pred = results.get_prediction(start=today,end=today+relativedelta(years=1), dynamic=False)
pred_ci = pred.conf_int()
df = pd.DataFrame(pred_ci)
dftojson=pd.DataFrame()
dftojson["Date"]=df.index
Approx_Price = (df["lower Modal_Price"].to_numpy() + df["upper Modal_Price"].to_numpy())
dftojson["Approx_price"] = Approx_Price/2
dftojson=dftojson.set_index('Date')
dftojson.to_csv('file1.csv')
csv_file = pd.DataFrame(pd.read_csv("file1.csv", sep = ",", header = 0, index_col = False))
predicted = csv_file.to_json("file.json", orient = "records", date_format = "epoch", double_precision = 10, force_ascii = True, date_unit = "ms", default_handler = None)

#File Upload
#Paddy(Dhan)(Common)
import requests 
myurl = 'http://localhost:8080/cpp/file/'
files = {'file': open('file.json', 'rb')}
cropname = input("Enter Crop Name : ") 
data = {"uploaded_by":"Nazneen Kiresur","cropname":cropname}
getdata = requests.post(myurl,data=data,files=files)
print(getdata.text)
