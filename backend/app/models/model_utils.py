import pandas as pd
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String, Integer, Float
import inspect

Base = declarative_base()

def create_model_class(table_name, columns):
    class_name = table_name.capitalize() + "Model"
    attributes = {
        "__tablename__": table_name,
        "id": Column(Integer, primary_key=True),
    }

    for column in columns:
        column_name = column["name"]
        column_type = column["type"]

        if column_type == "string":
            attributes[column_name] = Column(String)
        elif column_type == "integer":
            attributes[column_name] = Column(Integer)
        elif column_type == "float":
            attributes[column_name] = Column(Float)

    return type(class_name, (Base,), attributes)




def generate_class_declaration(obj, class_name):
    attributes = inspect.getmembers(obj)
    class_declaration = f"class {class_name}:\n"

    for attr_name, attr_value in attributes:
        if not attr_name.startswith('__') and not inspect.ismethod(attr_value):
            class_declaration += f"    {attr_name} = {repr(attr_value)}\n"

    return class_declaration



# Example usage


# Usage example
excel_file = "Metadata2.xlsx"
sheet_name = "Metadata"
database_url = "sqlite:///example.db"
table_name = "music_piece"
# table_name = "music_col"

MyModel = excel_to_sqlalchemy(excel_file, sheet_name, database_url, table_name)
class_declaration = generate_class_declaration(MyModel, "Music")
print(class_declaration) 
