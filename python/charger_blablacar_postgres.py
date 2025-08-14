import os
import sys
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import Integer, String, Date, Numeric, Text

# --------------- CONFIG ---------------
# Option A: DSN string (edit this line)
# Example: postgresql://user:password@localhost:5432/blablacar
DB_DSN = os.getenv("BLABLACAR_PG_DSN", "postgresql://postgres:postgres@localhost:5432/blablacar")

# CSV directory containing the files
CSV_DIR = Path(os.getenv("BLABLACAR_CSV_DIR", "./data"))

# If your requests.csv HAS a header row, set this to True
REQUESTS_HAS_HEADER = False

# Chunk size for to_sql (None means single batch)
CHUNK_SIZE = None
# ------------- END CONFIG -------------

def fail(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)

def normaliser_heure_hhmm(s: pd.Series) -> pd.Series:
    """Convert '7h32' -> '07:32', '19h02'->'19:02'; leave NaN as-is."""
    def _fix(x):
        if pd.isna(x):
            return x
        x = str(x).strip()
        if not x:
            return None
        x = x.replace("H", "h")
        if "h" not in x:
            return x  # unexpected, keep
        parts = x.split("h", 1)
        if len(parts) != 2:
            return x
        hh, mm = parts
        hh = hh.zfill(2)
        mm = mm.zfill(2)
        return f"{hh}:{mm}"
    return s.map(_fix)

def verifier_dossier(path: Path):
    if not path.exists():
        fail(f"CSV directory not found: {path.resolve()}")

def lire_csv_generique(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        fail(f"Missing CSV file: {path.name}")
    return pd.read_csv(path, **kwargs)

def principal():
    verifier_dossier(CSV_DIR)
    engine = create_engine(DB_DSN, future=True)

    # ---------- Load cars.csv ----------
    cars = lire_csv_generique(
        CSV_DIR / "cars.csv",
        dtype={"car_id": "Int64", "maker": "string", "CO2_code": "string", "colour": "string",
               "year": "Int64", "plate": "string"},
    ).rename(columns={"CO2_code": "co2_code"})
    cars = cars.astype({"car_id": "int64", "year": "Int64"})
    cars.to_sql(
        "cars", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={
            "car_id": Integer(), "maker": String(50), "co2_code": String(10), "colour": String(30),
            "year": Integer(), "plate": String(20)
        }
    )
    print(f"[OK] cars: {len(cars)} rows")

    # ---------- Load cities.csv ----------
    cities = lire_csv_generique(
        CSV_DIR / "cities.csv",
        dtype={"city_id": "Int64", "city_name": "string", "state": "string", "country": "string"},
    )
    cities = cities.astype({"city_id": "int64"})
    cities.to_sql(
        "cities", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={"city_id": Integer(), "city_name": String(60), "state": String(60), "country": String(60)}
    )
    print(f"[OK] cities: {len(cities)} rows")

    # ---------- Load luggage_types.csv ----------
    luggage = lire_csv_generique(
        CSV_DIR / "luggage_types.csv",
        dtype={"luggage_type_id": "Int64", "type": "string"},
    )
    luggage = luggage.astype({"luggage_type_id": "int64"})
    luggage.to_sql(
        "luggage_types", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={"luggage_type_id": Integer(), "type": String(15)}
    )
    print(f"[OK] luggage_types: {len(luggage)} rows")

    # ---------- Load members.csv ----------
    # Parse dates; allow non-zero padded months/days
    members = lire_csv_generique(
        CSV_DIR / "members.csv",
        dtype={"member_id": "string", "first_name": "string", "last_name": "string", "gender": "string",
               "mobile_number": "string", "email": "string",
               "is_ride_owner": "Int64", "license_driving_number": "string",
               "pet_preference": "string", "smoking_preference": "string", "bank_account": "string"},
        parse_dates=["inscription_date", "birthdate", "license_driving_date"],
        dayfirst=False, infer_datetime_format=True, keep_default_na=False, na_values=[""]
    )
    # Truncate gender to 1 char; ensure smallint for is_ride_owner
    members["gender"] = members["gender"].fillna("").str.strip().str[:1]
    members["is_ride_owner"] = members["is_ride_owner"].fillna(0).astype("Int64")

    members.to_sql(
        "members", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={
            "member_id": String(20), "first_name": String(60), "last_name": String(60),
            "gender": String(1), "mobile_number": String(30), "email": String(120),
            "inscription_date": Date(), "birthdate": Date(),
            "is_ride_owner": Integer(),
            "license_driving_number": String(40), "license_driving_date": Date(),
            "pet_preference": String(5), "smoking_preference": String(5),
            "bank_account": String(34)
        }
    )
    print(f"[OK] members: {len(members)} rows")

    # ---------- Load member_car.csv ----------
    member_car = lire_csv_generique(
        CSV_DIR / "member_car.csv",
        dtype={"member_car_id": "Int64", "member_id": "string", "car_id": "Int64"}
    ).astype({"member_car_id": "int64", "car_id": "int64"})
    member_car.to_sql(
        "member_car", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={"member_car_id": Integer(), "member_id": String(20), "car_id": Integer()}
    )
    print(f"[OK] member_car: {len(member_car)} rows")

    # ---------- Load request_status.csv ----------
    req_status = lire_csv_generique(
        CSV_DIR / "request_status.csv",
        dtype={"request_status_id": "Int64", "status": "string"}
    ).astype({"request_status_id": "int64"})
    req_status.to_sql(
        "request_status", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={"request_status_id": Integer(), "status": String(20)}
    )
    print(f"[OK] request_status: {len(req_status)} rows")

    # ---------- Load rides.csv ----------
    rides = lire_csv_generique(
        CSV_DIR / "rides.csv",
        dtype={"ride_id": "Int64", "member_car_id": "Int64", "departure_date": "string",
               "departure_time": "string", "starting_city_id": "Int64", "destination_city_id": "Int64",
               "number_seats": "Int64", "contribution_per_passenger": "float64", "luggage_id": "Int64"},
        keep_default_na=False, na_values=[""]
    )
    # Parse dates and normalize time
    rides["departure_date"] = pd.to_datetime(rides["departure_date"], errors="coerce").dt.date
    rides["departure_time"] = normaliser_heure_hhmm(rides["departure_time"])
    rides = rides.astype({
        "ride_id": "int64", "member_car_id": "int64", "starting_city_id": "int64",
        "destination_city_id": "int64", "number_seats": "Int64", "luggage_id": "Int64"
    })

    rides.to_sql(
        "rides", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={
            "ride_id": Integer(), "member_car_id": Integer(), "departure_date": Date(),
            "departure_time": String(5), "starting_city_id": Integer(), "destination_city_id": Integer(),
            "number_seats": Integer(), "contribution_per_passenger": Numeric(8,2),
            "luggage_id": Integer()
        }
    )
    print(f"[OK] rides: {len(rides)} rows")

    # ---------- Load requests.csv ----------
    req_cols = ["request_id", "ride_id", "requester_id", "request_status_id"]
    if REQUESTS_HAS_HEADER:
        requests_df = lire_csv_generique(
            CSV_DIR / "requests.csv",
            dtype={"request_id": "Int64", "ride_id": "Int64", "requester_id": "string", "request_status_id": "Int64"},
        )
    else:
        requests_df = lire_csv_generique(
            CSV_DIR / "requests.csv",
            header=None, names=req_cols,
            dtype={"request_id": "Int64", "ride_id": "Int64", "requester_id": "string", "request_status_id": "Int64"},
        )
    requests_df = requests_df.astype({"request_id": "int64", "ride_id": "int64", "request_status_id": "int64"})
    requests_df.to_sql(
        "requests", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={"request_id": Integer(), "ride_id": Integer(), "requester_id": String(20), "request_status_id": Integer()}
    )
    print(f"[OK] requests: {len(requests_df)} rows")

    # ---------- Load messages.csv ----------
    messages = lire_csv_generique(
        CSV_DIR / "messages.csv",
        dtype={"message_id": "string", "sender_id": "string", "receiver_id": "string", "body": "string"},
        quotechar='"'  # ensure quoted bodies with commas are read properly
    )
    messages.to_sql(
        "messages", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={"message_id": String(20), "sender_id": String(20), "receiver_id": String(20), "body": Text()}
    )
    print(f"[OK] messages: {len(messages)} rows")

    # ---------- Load ratings.csv ----------
    ratings = lire_csv_generique(
        CSV_DIR / "ratings.csv",
        dtype={"rating_id": "string", "rating_giver_id": "string", "rating_receiver_id": "string",
               "comments": "string", "grades": "Int64"},
        keep_default_na=False, na_values=[""]
    ).rename(columns={"grades": "grade"})
    ratings.to_sql(
        "ratings", engine, if_exists="append", index=False, chunksize=CHUNK_SIZE,
        dtype={
            "rating_id": String(20), "rating_giver_id": String(20), "rating_receiver_id": String(20),
            "comments": Text(), "grade": Integer()
        }
    )
    print(f"[OK] ratings: {len(ratings)} rows")

    # ---------- Sanity checks ----------
    with engine.connect() as conn:
        for tbl in ["cars","cities","luggage_types","members","member_car","request_status","rides","requests","messages","ratings"]:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar_one()
            print(f"[COUNT] {tbl}: {cnt}")

    print("\nAll done. ✅")

if __name__ == "__principal__":
    principal()
