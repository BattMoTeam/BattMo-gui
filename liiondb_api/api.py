from flask import Flask, request
from flask_restful import Resource, Api
import pandas as pd
import os
import sys

# sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("PAth = ", sys.path)
from liiondb.functions.fn_db import *
dfndb, db_connection = liiondb()

##############################
# Create flask api
############################

server = Flask(__name__)
api = Api(server)

def create_query(material_name):
    

    query = '''
            SELECT DISTINCT parameter.symbol,parameter.name as parameter, material.name as material,data.raw_data, parameter.units_output, paper.paper_tag, paper.doi
            FROM data
            JOIN paper ON paper.paper_id = data.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE material.name = '{}'
            '''.format(material_name)

    return query


class LiiondbQuery(Resource):

    def post(self):

        query_request = request.data.decode('utf-8')

        materials = {
            "Negative electrode Active material": ["Graphite", "Graphite-Silicon","Silicon"],
            "Positive electrode Active material": ["NMC552", "NMC811", "NMC","LFP","LCO","NMC111","LiNiO2","NMC523","NCO46","NCA","NMC622","NMC532","LMO","NMC71515","NMC442","LTO","NMC550"],
            "Electrolyte": ["LiPF6:PC", "LiPF6:EC:DMC:EMC 1:1:1", "LiPF6:PC:EC:DMC","LiPF6:EC:DEC 1:1" ,"LiPF6:EC:DMC 1:1","LiPF6:EC:EMC 1:1","LiPF6:EC:EMC 1:9","LiPF6:DMC","LiPF6:EC:DMC 2:1","LiPF6:EC:EMC 3:7","LiPF6:EC:DMC 2:8","LiClO4:EC:DEC 1:1","LiTFSI:ACN","LiPF6:EC:DMC 3:7","LiPF6:EC:DMC 2:1 in Polymer Matrix","LiPF6:EC:DEC 1:2","LiPF6:MA","LiPF6:EC:EMC 4:6","LiTFSI:PC","LiPF6:EMC","LiPF6:EC:DMC 1:2 in Polymer Matrix","LiPF6:EC:PC:DMC 5:2:3","LiPF6:Solvent","LiPF6:EC:DMC 1:2","LiPF6:EC:DEC:PMMA 1:1:0.15","LiPF6:EC:EMC 2:8","LiPF6:EC:DMC 1:9","LiPF6:EMC:FEC 19:1"],
            "Separator": ["Polymer Separator","glass fibre separator"]
        }

        material_names = materials[query_request]

        data_df = pd.DataFrame()

        for name in material_names:

            QUERY = create_query(name)

            df = pd.read_sql(QUERY, dfndb)

            data_df = pd.concat([data_df, df], ignore_index=True)


        df_json = data_df.to_json()

        return df_json



api.add_resource(LiiondbQuery, '/')
