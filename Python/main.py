import pandas as pd
import numpy as np
from functions import *
import matplotlib.pyplot as plt

#data set: https://www.kaggle.com/datasets/usdot/flight-delays

#-----------------------importul unei fișier csv în pachetul pandas
data_flights = pd.read_csv('flights.csv')
data_airports = pd.read_csv('airports.csv')
data_airlines = pd.read_csv('airlines.csv')

indicatori =  list(data_flights)[2:]

#-----------------------tratarea valorilor lipsa
print("Before nan replace")
total = data_flights.isna().sum().sort_values(ascending=False)
percent = (data_flights.isnull().sum()*100/data_flights.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
print(missing_data.head(20))

nan_replace_t(data_flights)

print("After nan replace")
total = data_flights.isna().sum().sort_values(ascending=False)
percent = (data_flights.isnull().sum()*100/data_flights.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
print(missing_data.head(20))





#-----------------------prelucrarea seturilor de date cu merge
data_flights2 = data_flights[indicatori].merge(data_airlines["AIRLINE"],left_index=True,right_index=True)
data_flights2.to_csv("flights2.csv")




# --------------------  prelucrări statistice, gruparea și agregarea datalor în pachetul pandas +
#                       utilizarea funcțiilor de grup +
#                       accesarea datelor cu loc și iloc;

#statistici descriptive
print("Descriptive statistics:")
df = pd.DataFrame(data_flights.describe())
df.to_csv("DescriptiveStatistics.csv")

#1. zboruri intarziate in anul 2015
delayed_in_2015 = data_flights.loc[data_flights['DEPARTURE_DELAY'] > 0]
count_delayed_in_2015 = delayed_in_2015['DEPARTURE_DELAY'].count()
print('Delayed in 2015:', count_delayed_in_2015)

#2. ziua din saptamana cu numar maxim de intarzieri in minute
days_groups = delayed_in_2015.groupby(['DAY_OF_WEEK']).count().reset_index()
max_delay = days_groups['DEPARTURE_DELAY'].max()
num_of_day = int(days_groups[days_groups.DEPARTURE_DELAY == max_delay].DAY_OF_WEEK)
day_of_week = day_name(num_of_day)
print('Day of week with max delayed:', day_of_week)

# suma de intarzieri pe fiecare zi din sapt
days_groups_sum = delayed_in_2015.groupby(['DAY_OF_WEEK']).agg(sum)
df_delayed_days = pd.DataFrame(days_groups_sum)
df_delayed_in_hours = minutes_to_hours(df_delayed_days)
df_delayed_in_hours['DEPARTURE_DELAY'].to_csv('TimeDelayedByDay.csv')
#3. distanta maxima parcursa
max_distance = data_flights["DISTANCE"].max()
print('Distance:', max_distance)
#6. zboruri anulate
cancelled_flights = data_flights.loc[data_flights['CANCELLED'] == 1]
count_cancelled_flights = cancelled_flights['CANCELLED'].count()
print('Cancelled in 2015:',count_cancelled_flights)
#7. motive pentru anularea zborurilor
cancelled_reasons = cancelled_flights.groupby(['CANCELLATION_REASON'],sort=False).count().reset_index()
df_cancelled_reasons = pd.DataFrame(cancelled_reasons)
df_cancelled_reasons.to_csv("CancelledReasons.csv")
max_for_reason = cancelled_reasons['Unnamed: 0'].max()
common_reason = list(cancelled_reasons[cancelled_reasons.CANCELLED == max_for_reason].CANCELLATION_REASON)
print("The most common reason for canceling is: ", common_reason[0])

#cel mai comun motiv pentru anulare este B - Weather , 10630 de zboruri au fost anulate din acest  motiv
#urmatorul cel mai comun motiv  A - Airline/Carrier cu 3230 zboruri anulate,
#mai apoi C - National Air System  cu 2962 zboruri anulate
#ultimul fiind D - Security cu doar 2 anulari

#8. Procent zboruri anulate
percentage_of_canceled= (count_cancelled_flights / data_flights['FLIGHT_NUMBER'].count())*100
print("Procent of cancelled flights: ", np.round(percentage_of_canceled,2))


# #9. Distanta maxima si minima a zborurilor anulate
# max_distance_in_cancelled = cancelled_flights["DISTANCE"].max()
# min_distance_in_cancelled = cancelled_flights["DISTANCE"].min()
# cancelled_flights.to_csv("CanceledFlights.csv")
#
#
# cancelled_flights_with_min_distance = cancelled_flights.loc[cancelled_flights.DISTANCE == min_distance_in_cancelled]
# origin_airport = cancelled_flights_with_min_distance.ORIGIN_AIRPORT.unique()
# dest_airport = cancelled_flights_with_min_distance.DESTINATION_AIRPORT.unique()
# airport_full_name_origin = list(data_airports[data_airports.IATA_CODE.isin(origin_airport)].AIRPORT)
# airport_full_name_dest = list(data_airports[data_airports.IATA_CODE.isin(dest_airport)].AIRPORT)
# print('Shortest path: from {} to {}'.format(airport_full_name_origin[0], airport_full_name_dest[0]))
#
# cancelled_flights_with_max_distance = cancelled_flights.loc[cancelled_flights.DISTANCE == max_distance_in_cancelled]
# origin_airport = cancelled_flights_with_max_distance.ORIGIN_AIRPORT.unique()
# dest_airport = cancelled_flights_with_max_distance.DESTINATION_AIRPORT.unique()
# airport_full_name_origin = list(data_airports[data_airports.IATA_CODE.isin(origin_airport)].AIRPORT)
# airport_full_name_dest = list(data_airports[data_airports.IATA_CODE.isin(dest_airport)].AIRPORT)
# print('Longest path: from {} to {}'.format(airport_full_name_origin[0], airport_full_name_dest[0]))

#--------------------------------------
#4. zboruri cu distanta maxima -> aeroport sursa
flights_with_max_distance = data_flights[data_flights.DISTANCE == max_distance]
ORIGIN_AIRPORT = flights_with_max_distance.ORIGIN_AIRPORT.unique()
DESTINATION_AIRPORT = flights_with_max_distance.DESTINATION_AIRPORT.unique()
FULL_NAME_ORIGIN = list(data_airports[data_airports.IATA_CODE.isin(ORIGIN_AIRPORT)].AIRPORT)
FULL_NAME_DESTINATION = list(data_airports[data_airports.IATA_CODE.isin(DESTINATION_AIRPORT)].AIRPORT)
print('Airports full name (origin) :',FULL_NAME_ORIGIN)
print('Airports full name (destination) :',FULL_NAME_DESTINATION)


#5. codul zborurilor si al aeronavelor de la compania JetBlue care au avut intarziere in anul 2015
IATA_CODE_OF_JET = list(data_airlines[data_airlines['AIRLINE'] == 'JetBlue Airways'].IATA_CODE)
JET_TAILS_NUMBERS = delayed_in_2015.loc[delayed_in_2015['AIRLINE'] == IATA_CODE_OF_JET[0]].TAIL_NUMBER
JET_TAILS_NUMBERS.to_csv("TailNumbersForJetDelayedIn2015.csv")
print("First 10 Jet tails numbers for company JetBlue that had delayes in 2015:")
print(JET_TAILS_NUMBERS.iloc[0:10,])

#--------------------------- utilizarea listelor, tuplurilor + iloc
# Create a list of tuples of latitude and longitude and a list to store the IATA code
lat_lon_pairs = []
airport_code = []
for i in range(data_airports.shape[0]):
        # Adding lat lon pairs
        lat_i = data_airports['LATITUDE'].iloc[i]
        lon_i = data_airports['LONGITUDE'].iloc[i]
        lat_lon_pair = (lat_i, lon_i)
        lat_lon_pairs.append(lat_lon_pair)

        # Addinf IATA Code
        iata_i = data_airports['IATA_CODE'].iloc[i]
        airport_code.append(iata_i)

print("IATA CODES",airport_code)
print("LATITUDE LONGITUDE TUPLE",lat_lon_pairs)


flights_data = pd.merge(left = data_flights, right = data_airlines, left_on='AIRLINE', right_on='IATA_CODE')
top_10_origin_airports = flights_data['ORIGIN_AIRPORT'].value_counts().sort_values().iloc[-10:].index

# Find lat longs of top 10 origin airports
top_10_origin_airports_lat_lon = []
for airport in top_10_origin_airports:
        lat = data_airports[data_airports['IATA_CODE'] == airport]['LATITUDE']
        lon = data_airports[data_airports['IATA_CODE'] == airport]['LONGITUDE']

        lat_lon = (lat, lon)
        top_10_origin_airports_lat_lon.append(lat_lon)
print("LATITUDE LONGITUDE for top 10 origin airports")
print(list(top_10_origin_airports_lat_lon))


#regresie logistică
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def set_isDelayed(x):
    if x > 0:
        return 1
    else:
        return 0


data_flights['IS_DELAYED'] = data_flights['DEPARTURE_DELAY'].apply(set_isDelayed)

list_numeric =data_flights.select_dtypes(include=np.number).columns.tolist()
list_non_numeric =  data_flights.select_dtypes(exclude=np.number).columns.tolist()
print('Coloane numerice', list_numeric)
print('Coloane non-numerice', list_non_numeric)
list_numeric.remove("Unnamed: 0")
list_numeric.remove("IS_DELAYED")


# Extragerea variabilelor x si a variabilei target y din setul de date
x = data_flights[list_numeric]
y = data_flights['IS_DELAYED']

X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=1, test_size=.20)

#Aplicarea modelului de REGRESIE LOGISTICA
RL = LogisticRegression(max_iter=50, multi_class='ovr', penalty='l2',  solver='lbfgs')
RL.fit(X_train, y_train)
y_predicted = RL.predict(X_test)


#Verificarea modelului de regresie logistica.
#Afisam acuratetea, matricea de confuzie şi raportul de clasificare
CM=confusion_matrix(y_test, y_predicted)
print("Confusion matrix:")
print(CM)
conf_mtrx(y_test, y_predicted, 'RL')
RL_report=classification_report(y_test, y_predicted)
print("Classification report:")
print(RL_report)
acuratetea_RL=accuracy_score(y_test, y_predicted)
print("Acuratetea RL: ", acuratetea_RL)
roc_auc_curve_plot(RL, X_test, y_test)


#--------------------------------reprezentare grafică a datelor cu pachetul matplotlib
#1
days =['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
x1 = days
y1 = list(days_groups['DEPARTURE_DELAY'])
plt.xlabel('Week day')
plt.ylabel('Number of delayed flights')
plt.title('Delayed flights in 2015')
plt.bar(x1,y1)
plt.show()

#2
labels ='Cancelled', 'Non-Cancelled'
sizes = [percentage_of_canceled, 100-percentage_of_canceled]
explode = (0, 0.1)
colors = ['gold', 'lightskyblue']
fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels,colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')
ax1.set_title('Percentage of canceled flights in 2015\n')

plt.show()
#3
x2= ['Delayed','Cancelled']
y2= [count_delayed_in_2015,count_cancelled_flights]
plt.xlabel('Number of Flights')
plt.ylabel('s')
plt.barh(x2,y2)
plt.title('Delayed vs cancelled flights in 2015')
plt.show()

#4
reason_counts = cancelled_flights['CANCELLATION_REASON'].value_counts()
reasons=[3230,10630,2962,2]

plt.title('Cancellation reasons')
colors = {'A - Airline/Carrier':'red', 'B - Weather':'green', 'C - National Air System ':'yellow',' D - Security':'purple'}
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

# data
x = ['A','B','C','D']
c = ['red', 'green', 'yellow', 'purple']

# bar plot
plt.bar(x, height=reasons, color=c)

plt.show()


#5
days =['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
x1 = days
y1 = list(df_delayed_in_hours['DEPARTURE_DELAY'])
plt.xlabel('Week day')
plt.ylabel('Time delayed(hours) ')
plt.title('Total time delaying by week day')
plt.bar(x1,y1)
plt.show()