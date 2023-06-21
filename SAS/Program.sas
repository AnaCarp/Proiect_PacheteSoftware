/*------------------Creare set de date SAS din fisiere externe----------------------------- */

DATA airlines;
	INFILE '/home/u63359316/Proiect/airlines.csv' DSD;
	LENGTH AIRLINE $27;
	INPUT IATA_CODE $ AIRLINE;
RUN;


DATA airports;
	INFILE '/home/u63359316/Proiect/airports.csv' DSD;
	INPUT IATA_CODE $ AIRPORT $ CITY $ STATE $ COUNTRY $ LATITUDE LONGITUDE;
RUN;


DATA flights;
	INFILE '/home/u63359316/Proiect/flights.csv' DSD;
	INPUT 	YEAR	MONTH	DAY	DAY_OF_WEEK	AIRLINE $	FLIGHT_NUMBER	TAIL_NUMBER $	
	ORIGIN_AIRPORT $ DESTINATION_AIRPORT $	SCHEDULED_DEPARTURE	DEPARTURE_TIME	
	DEPARTURE_DELAY	TAXI_OUT	WHEELS_OFF	SCHEDULED_TIME	ELAPSED_TIME	AIR_TIME	
	DISTANCE	WHEELS_ON	TAXI_IN	SCHEDULED_ARRIVAL	ARRIVAL_TIME	ARRIVAL_DELAY	
	DIVERTED	CANCELLED	CANCELLATION_REASON	AIR_SYSTEM_DELAY	SECURITY_DELAY	AIRLINE_DELAY	
	LATE_AIRCRAFT_DELAY	WEATHER_DELAY;
RUN; 


/*---------------------------------Crearea formatelor definite de utilizator------------------------*/


proc format;
    value $AIRLINE
    'United Air Lines Inc.' = 'United'
    'American Airlines Inc.' = 'American'
    'Southwest Airlines Co.' = 'Southwest'
    'Virgin America' = 'Virgin'
    other='Other';
run;


proc format;
  value DEPARTURE_DELAY
  0 = 'On time'
  1-15 = 'Slight delay'
  16-60 = 'Moderate delay'
  61-9999 = 'Severe delay';
run;

/* Aplicarea formatele definite de utilizator */

data airlines_formatted;
    set airlines;
    format AIRLINE $AIRLINE.;
run;


data flights_formatted;
  set flights;
  format DEPARTURE_DELAY DEPARTURE_DELAY.;
run;

/*---------------------------------Crearea de subseturi------------------------*/

/* Subset 1. pentru zboruri cu întârziere la decolare mai mare de 30 de minute */
data delayed_departures;
  set flights;
  where DEPARTURE_DELAY > 30;
run;

/* Subset 2. pentru zboruri cu întârziere la aterizare mai mare de 15 minute */
data delayed_arrivals;
  set flights;
  where ARRIVAL_DELAY > 15;
run;

/* Subset 3. pentru zboruri din aeroportul JFK si cu o întârziere la decolare mai mare de 120 de minute */
data jfk_flights;
	set flights;
	where ORIGIN_AIRPORT = 'JFK' and DEPARTURE_DELAY > 120;
run;


/*Subset 4. care să conțină doar informațiile despre zborurile care au avut întârziere la sosire mai mare de 1 oră și care nu au fost anulate.*/
data delayed_flights;
	set flights (keep=YEAR MONTH DAY AIRLINE FLIGHT_NUMBER ORIGIN_AIRPORT DESTINATION_AIRPORT ARRIVAL_DELAY CANCELLED);
	where ARRIVAL_DELAY > 60 and CANCELLED = 0;
run;

/*Subset 5. care să conțină zborurile operate de linia AA si care au aeroportul de origine JFK*/
data flights_subset;
  set flights;
  where AIRLINE = 'AA' and ORIGIN_AIRPORT = 'JFK';
run;



/*---------------------------------Grafice + Proceduri SQL------------------------*/

********************************Graficul cu zboruri întârziate în funcție de ziua săptămânii;
proc sort data=flights;
    by DAY_OF_WEEK;
run;


proc sql;
    create table delayed_flights_by_day as
    select DAY_OF_WEEK, count(*) as delayed_flights
    from flights
    where ARRIVAL_DELAY > 0
    group by DAY_OF_WEEK;
quit;

proc sgplot data=delayed_flights_by_day;
    vbar DAY_OF_WEEK / response=delayed_flights barwidth=0.5 datalabel;
    xaxis discreteorder=data;
    yaxis grid;
    title 'Zboruri întârziate în functie de ziua săptămânii';
run;




/* Proceduri SQL + procesarea iterativă și condițională a datelor */
/*Numarul de zboruri anulate */
proc sql;
    select count(*) as Numar_Anulate
    from flights
    where CANCELLED = 1;
quit;

/* Medie și deviație standard a timpului de decolare pentru zborurile de la un anumit aeroport dintr-un anumit stat și țară */
proc sql;
    select ORIGIN_AIRPORT, STATE, COUNTRY, mean(DEPARTURE_DELAY) as Medie, std(DEPARTURE_DELAY) as Deviatie_Standard
    from flights
    inner join airports on flights.ORIGIN_AIRPORT = airports.IATA_CODE
    where airports.STATE = 'NY' and airports.COUNTRY = 'USA'
    group by ORIGIN_AIRPORT, STATE, COUNTRY;
quit;

/* Exercițiul 2 IF: Medie și deviație standard a timpului de decolare pentru zborurile de la un anumit aeroport dintr-un anumit stat și țară folosind structură condițională IF */
data medie_deviatie;
    set flights;
    if STATE = 'NY' and COUNTRY = 'USA' then do;
        sum_departure_delay + DEPARTURE_DELAY;
        count_zboruri + 1;
    end;
run;
data medie_deviatie;
    set medie_deviatie;
    if count_zboruri > 0 then do;
        medie = sum_departure_delay / count_zboruri;
        std = sqrt((sum_departure_delay_square - count_zboruri * medie ** 2) / (count_zboruri - 1));
    end;
run;
proc print data=medie_deviatie(obs=20);
run;

/*Să se adauge o nouă variabilă în setul de date "flights" 
care să indice dacă un zbor a fost întârziat sau nu, în funcție 
de valoarea variabilei "DEPARTURE_DELAY"*/

data flights;
    set flights;
    if DEPARTURE_DELAY > 0 then do;
        is_delayed = 1;
    end;
    else do;
        is_delayed = 0;
    end;
run;

proc print data=flights(obs=20);
run;

/*Să se identifice zborurile care au avut loc în aeroporturi din New York (STATE = 'NY') și să se 
creeze un nou set de date care să conțină doar aceste zboruri:*/
data flights_ny;
    set flights;
    if ORIGIN_AIRPORT in ('JFK', 'LGA') or DESTINATION_AIRPORT in ('JFK', 'LGA') then do;
        output;
    end;
run;

proc print data=flights_ny (obs=20);
run;


/* cele mai ocupate 5 aeroporturi de plecare pe baza numărului total de zboruri (num_flights) din setul de date combinat*/
proc sql;
    create table combined as
    select f.*, a.LATITUDE, a.LONGITUDE
    from flights as f
    left join airports as a
    on f.ORIGIN_AIRPORT = a.IATA_CODE;
quit;

/* Exemplu de analiza pe baza setului de date combinat */
proc sql;
    create table top_origin_airports as
    select ORIGIN_AIRPORT, count(*) as num_flights
    from combined
    group by ORIGIN_AIRPORT
    order by num_flights desc;
quit;

/* Afisare rezultate */
proc print data=top_origin_airports (obs=5);
    title "Top 5 aeroporturi de plecare (ORIGIN_AIRPORT)";
run;

/*Proceduri statistice SAS*/

proc means data=flights mean median min max;
  var DEPARTURE_DELAY;
run;

proc freq data=airports;
  tables COUNTRY / nocum nopercent;
run;
proc univariate data=flights;
  var DISTANCE;
  histogram / normal;
run;

/*regresie*/
PROC CORR  data=flights;
	VAR DEPARTURE_DELAY;
	WITH ARRIVAL_DELAY;
	TITLE "Corelatia intre ARRIVAL_DELAY de DEPARTURE_DELAY";
RUN;
proc reg data=flights;
  model ARRIVAL_DELAY = DEPARTURE_DELAY;
  PLOT ARRIVAL_DELAY*DEPARTURE_DELAY;
	TITLE "Rezultatele analizei de regresie";
run;


