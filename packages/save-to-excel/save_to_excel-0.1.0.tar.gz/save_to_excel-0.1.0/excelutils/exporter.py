import pandas as pd

def save_to_excel(filename, obj):
    """
    filename : Excel file name (Data.xlsx)
    obj      : MongoDB collection or iterable of dicts
    """
    try:
        # If obj is MongoDB collection
        if hasattr(obj, "find"):
            data = list(obj.find({}, {"_id": 0}))
        else:
            data = list(obj)

        if not data:
            print("No data to write")
            return

        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Data saved successfully to {filename}")

    except Exception as e:
        print("Error saving Excel file:", e)
