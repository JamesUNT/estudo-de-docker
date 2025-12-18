#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'

@click.command()
@click.option('--pg-user', default='root', help='Postgres User')
@click.option('--pg-password', default='root', help='Postgres Password')
@click.option('--pg-host', default='localhost', help='Postgres Host')
@click.option('--pg-port', default='5432', help='Postgres Port')
@click.option('--pg-db', default='ny_taxi', help='Postgres Database')
@click.option('--year', default=2021, help='Year of data')
@click.option('--month', default=1, help='Month of data')
@click.option('--chunksize', default=100000, help='Chunk size')
@click.option('--target-table', default='yellow_taxi_trips', help='Target table')

def run(pg_user, pg_password, pg_host, pg_port, pg_db, year, month, chunksize, target_table):
    
    target_table = f"{target_table}_{year}_{month:02d}"

    first_chunk = True

    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'

    df = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates
    )

    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    for df in tqdm(df_iter):
        if first_chunk:
            df.head(0).to_sql(name=target_table, con=engine, if_exists='replace')
            first_chunk = False
        df.to_sql(name=target_table, con=engine, if_exists='append')


if __name__ == '__main__':
    run()
