import requests
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

def normalizar_nombre_barrio(nombre):
    # Convertir todo a minúsculas
    nombre = nombre.lower()
    # Reemplazar acentos por caracteres sin acento
    nombre = nombre.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    # Reemplazar "S." por "San" en cualquier parte del nombre
    nombre = nombre.replace('s.lluis', 'san luis')
    # Eliminar el punto intermedio (·)
    nombre = nombre.replace('marcel.li', 'marceli')  # Eliminamos el punto intermedio
    # Eliminar el guion (-) para hacer los nombres equivalentes
    nombre = nombre.replace('-', '')  # Eliminamos el guion
    # Si es necesario, manejar otras reglas de normalización adicionales aquí...
    return nombre

def obtener_mongo(collection_name):
    client = MongoClient("mongodb://root:example@mongo:27017/")
    db = client["Dataproject1"]
    collection = db[collection_name]
    document = collection.find_one(sort=[("_id", -1)])
    return document

def get_data():
    # Conexión a las conexiones
    geo = obtener_mongo("geo")
    alquiler = obtener_mongo("precio_alquiler")
    compra = obtener_mongo("precio_compra")
    metro = obtener_mongo("metro")
    bus = obtener_mongo("bus")
    vulne = obtener_mongo("vulnerabilidad")
    hospi = obtener_mongo("hospitales")
    parques = obtener_mongo("zonas_infantiles")

    # Geo
    df_geo = pd.DataFrame([
            {
                "id": record["coddistbar"],
                "barrio": record["nombre"],
                "geometry": record["geo_shape"]["geometry"],
                "lat": record["geo_point_2d"]["lat"],
                "lon": record["geo_point_2d"]["lon"]
            }
            for record in geo["results"]
        ])

    # Alquiler
    df_alquiler = pd.DataFrame([
            {
                "id": record["codbar_coddistrit"],
                "precio_alquiler": record["precio_alquiler_m2"]
            }
            for record in alquiler["results"]
        ])

    min_alquiler = df_alquiler['precio_alquiler'].min()
    max_alquiler = df_alquiler['precio_alquiler'].max()

    df_alquiler['precio_alquiler_normalizado'] = 1 - (df_alquiler['precio_alquiler'] - min_alquiler) / (max_alquiler - min_alquiler)

    # Compra
    df_compra = pd.DataFrame([
            {
                "id": record["coddistbar"],
                "precio_compra": record["precio_compra_m2"]
            }
            for record in compra["results"]
        ])

    min_compra = df_compra['precio_compra'].min()
    max_compra = df_compra['precio_compra'].max()

    df_compra['precio_compra_normalizado'] = 1 - (df_compra['precio_compra'] - min_compra) / (max_compra - min_compra)

    # Metro
    df_metro = pd.DataFrame([
            {
                "id": record["coddistbar"],
                "paradas_metro": record["paradas_metro"]
            }
            for record in metro["results"]
        ])

    min_metro = df_metro['paradas_metro'].min()
    max_metro = df_metro['paradas_metro'].max()

    df_metro['paradas_metro_normalizado'] = (df_metro['paradas_metro'] - min_metro) / (max_metro - min_metro)

    # Bus
    df_bus = pd.DataFrame([
            {
                "id": record["coddistbar"],
                "paradas_bus": record["paradas_bus"]
            }
            for record in bus["results"]
        ])

    min_bus = df_bus['paradas_bus'].min()
    max_bus = df_bus['paradas_bus'].max()

    df_bus['paradas_bus_normalizado'] = (df_bus['paradas_bus'] - min_bus) / (max_bus - min_bus)

    # Vulnerabilidad
    df_vulne = pd.DataFrame([
            {
                "id": record["codbar"],
                "vulne": record["vulnerabilildad"]
            }
            for record in vulne["results"]
        ])

    min_vulne = df_vulne['vulne'].min()
    max_vulne = df_vulne['vulne'].max()

    df_vulne['vulne_normalizado'] = 1 - (df_vulne['vulne'] - min_vulne) / (max_vulne - min_vulne)

    # Hospitales
    df_hospi = pd.DataFrame([
            {
                "id": record["coddistbar"],
                "hospitales": record["hospitales"]
            }
            for record in hospi["results"]
        ])
    
    df_hospi['hospitales_normalizado'] = df_hospi['hospitales'] / 2

    # Parques
    df_parques = pd.DataFrame([
        {
            "barrio": record["barrio"],
            "cuenta": record["count(objectid)"]
        }
        for record in parques["results"]
    ])

    # Normalizar los nombres de los barrios para compararlos fácilmente
    df_geo["nombre_barrio"] = df_geo["barrio"].apply(normalizar_nombre_barrio)
    df_parques["nombre_barrio"] = df_parques["barrio"].apply(normalizar_nombre_barrio)

    # Realizar el merge entre los DataFrames por el nombre del barrio
    parques_merged = pd.merge(
        df_geo[['id', 'nombre_barrio']],
        df_parques,
        on="nombre_barrio",
        how="left"  # Mantener todos los barrios aunque no tengan zonas infantiles
    )
    
    min_parques = parques_merged['cuenta'].min()
    max_parques = parques_merged['cuenta'].max()
    parques_merged['parques_normalizado'] = 1 - (parques_merged['cuenta'] - min_parques) / (max_parques - min_parques)
    parques_merged = parques_merged.fillna(0)
    parques_merged = parques_merged.drop(columns=["barrio", "nombre_barrio", "cuenta"])
    df_parques = parques_merged.rename(columns={"parques_normalizado": "parques_infantiles"})

    # Merges
    df_geo['id'] = df_geo['id'].astype(int)
    df_alquiler['id'] = df_alquiler['id'].astype(int)
    df_compra['id'] = df_compra['id'].astype(int)
    df_metro['id'] = df_metro['id'].astype(int)
    df_bus['id'] = df_bus['id'].astype(int)
    df_vulne['id'] = df_vulne['id'].astype(int)
    df_hospi['id'] = df_hospi['id'].astype(int)
    df_parques['id'] = df_parques['id'].astype(int)

    df_base = pd.merge(df_geo, df_alquiler, on='id', how='left')
    df_base = pd.merge(df_base, df_compra, on='id', how='left')
    df_base = pd.merge(df_base, df_metro, on='id', how='left')
    df_base = pd.merge(df_base, df_bus, on='id', how='left')
    df_base = pd.merge(df_base, df_vulne, on='id', how='left')
    df_base = pd.merge(df_base, df_hospi, on='id', how='left')
    df_base = pd.merge(df_base, df_parques, on='id', how='left')

    df_base = df_base.fillna(0)
    df_base = df_base[df_base['precio_compra'] != 0]

    df_base = df_base[['id', 'barrio', 'geometry', 'lat', 'lon', 'precio_alquiler_normalizado', 'precio_compra_normalizado', 'paradas_metro_normalizado', 'paradas_bus_normalizado', 'vulne_normalizado', 'hospitales_normalizado','parques_infantiles']]

    df_base = df_base.rename(columns={
        'precio_alquiler_normalizado': 'el precio del alquiler',
        'precio_compra_normalizado': 'el precio de compra',
        'paradas_metro_normalizado': 'las paradas de metro',
        'paradas_bus_normalizado': 'las paradas de autobús',
        'vulne_normalizado': 'la tasa de vulnerabilidad',
        'hospitales_normalizado': 'los hospitales cercanos',
        'parques_infantiles': 'los parques infantiles cercanos'
    })

    return df_base

def get_mapa(df):
    # Creamos geojson para que luego lo pueda utilizar plotly
    geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "id": row["id"]
            },
            "geometry": row["geometry"]
        }
        for _, row in df.iterrows() # va fila a fila del df ignorando índices
    ]
    }

    # Mapa
    # https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth_mapbox.html#:~:text=a%20Mapbox%20map.-,Parameters,-data_frame%20(DataFrame
    mapa = px.choropleth_mapbox(
        df, # dataframe
        geojson=geojson, # geojson
        locations="id", # key para cruzar df con geojson
        featureidkey="properties.id",  # key para cruzar geojson con df
        color="valoración",  # Métrica para los colores
        color_continuous_scale=[(0, "azure"), (1, "seagreen")],
        hover_name="barrio",
        mapbox_style="carto-positron",
        center={"lat": 39.47, "lon": -0.37},
        zoom=11.5,
        height=600
    )
    
    mapa.update_layout(coloraxis_showscale=False)
    
    return mapa

def ponderar(respuestas, df_base):
    # Generamos las ponderaciones para que multiplique
    ponderaciones = { 
        0: 0,
        1: 0.5, 
        2: 0.75, 
        3: 1, 
        4: 1.25, 
        5: 1.50
        }

    # Creamos un nuevo diccionario
    # Este diccionario es como respuestas pero con los valores por los que queremos multiplicar luego
    respuestas_ponderadas = {
        factor: ponderaciones[valoracion] # accedemos al valor en ponderaciones cuya key equivale a lo que se ha respondido
        for factor, valoracion in respuestas.items() # .items devuelve los pares del diccionario
        }

    # Lista de los factores
    factores = ['el precio del alquiler', 'el precio de compra', 'las paradas de metro', 'las paradas de autobús','la tasa de vulnerabilidad','los hospitales cercanos','los parques infantiles cercanos']

    # Hacemos una copia del dataframe para que pondere luego
    df_ponderado = df_base.copy()

    # iloc [filas, columnas] -> cogemos solo las columnas numericas
    df_ponderado.iloc[:, 5:12] *= [respuestas_ponderadas[factor] # busca el número por el que hay que multiplicar para cada factor
                                for factor in factores] # itera sobre la lista inicial de factores sobre la que se basa el formulario

    # añadimos una columna de sumatorio de todos los factores
    df_ponderado['valoración'] = (df_ponderado.iloc[:, 5:12].sum(axis=1))

    # ordenamos de manera descendente
    df_ponderado = df_ponderado.sort_values(by='valoración', ascending=False)

    return df_ponderado