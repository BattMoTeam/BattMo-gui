from flask import Flask, request
from flask_restful import Resource, Api
import pandas as pd
import os
import sys

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from liiondb.functions.fn_db import *
dfndb, db_connection = liiondb()

##############################
# Create flask api
############################

server = Flask(__name__)
api = Api(server)

def create_query():

    query = '''
            SELECT DISTINCT data.data_id,parameter.symbol,parameter.name as parameter, material.name as material,data.raw_data, parameter.units_input, parameter.units_output, paper.paper_tag, paper.doi
            FROM data
            JOIN paper ON paper.paper_id = data.paper_id
            JOIN material ON material.material_id = data.material_id
            JOIN parameter ON parameter.parameter_id = data.parameter_id
            WHERE parameter.name = 'half cell ocv'
            AND material.lfp = 1
            LIMIT 5
            '''

    return query


class LiiondbQuery(Resource):

    def get(self):

        query_request = request.data.decode('utf-8')

        # QUERY = create_query(query_request)

        df = pd.read_sql(query_request, dfndb)
        df_json = df.to_json()

        return df_json



api.add_resource(LiiondbQuery, '/')
