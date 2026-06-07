
# Restauranter i København

Starterprojekt til TripAdvisor European Restaurants-datasættet.

Appen gør tre ting:

1. Først læser CSV-filen med pandas.
2. Derefter importerer relevante kolonner til SQLite.
3. Viser alle restauranter/steder i København via Flask web app.

## 1. Projektstruktur

```text
Restauranter i København/
├── app.py
├── import_data.py
├── requirements.txt
├── restaurants.db              
├── data/
│   └── tripadvisor_european_restaurants.csv
└── templates/
    └── index.html
```

## 2. Installation

Det her er fra projektmappen:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## 3. Læg datasættet ind
datasættet er ikke indkluderet i denne reseptprie da filen var for stor.
vi har hentet datasættet fra kaggle
link: https://www.kaggle.com/datasets/stefanoleone992/tripadvisor-european-restaurants
Det skal downloades manuelt fra Kaggle og placeres i mappen `data/` som:
data/tripadvisor_european_restaurants.csv


## 4. Importér data til SQLite

```bash
python import_data.py
```

Dette opretter databasen:

```text
restaurants.db
```

## 5. Start Flask-appen

```bash
flask --app app run --debug
```

Nu, kan man åbne siden i browseren:

```text
http://127.0.0.1:5000
```


Vi bruger SQL i `app.py` som her:

```sql
SELECT restaurant_name, city, country, address, avg_rating,
       total_reviews_count, price_level, cuisines, restaurant_link
FROM restaurants
WHERE lower(country) = 'denmark'
  AND (
    lower(city) = 'copenhagen'
    OR lower(city) = 'københavn'
    OR lower(original_location) LIKE '%copenhagen%'
    OR lower(original_location) LIKE '%københavn%'
  )
ORDER BY avg_rating DESC, total_reviews_count DESC
LIMIT 300;
```

Det er denne query, der henter stederne i København.

## 7. API endpoint

Der er også et simpelt JSON endpoint:

```text
/api/copenhagen
```

## Requirements

- Python 3.10+
- pandas
- flask
- sqlite3 (built-in)

