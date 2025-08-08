import pandas as pd
import os

DATA_DIR = "data"

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_to_csv(filename, data, columns):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df = pd.concat([df, pd.DataFrame([data], columns=columns)], ignore_index=True)
    else:
        df = pd.DataFrame([data], columns=columns)
    df.drop_duplicates(inplace=True)
    df.to_csv(file_path, index=False)

def load_csv(filename, columns):
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=columns)