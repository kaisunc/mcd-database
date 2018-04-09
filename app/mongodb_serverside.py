"""
http://datatables.net/forums/discussion/13679/working-code-for-server-side-paging-filtering-sorting-for-python-flask-mongodb
I wrote a python script for implementing server-side DataTables using python, flask, and mongodb. It works very well for me, so I thought I'd share the code for anyone that needs it. Below is the script generalized as a template for you guys. 

by luv_tables
January 2013
"""

from collections import namedtuple
from pymongo import MongoClient
from flask import request
from core.web.site import app
from core.web.site.views_master import *
import json
 
__author__ = 'spacecowboy / jkim'
 
# translation for sorting between datatables api and mongodb
order_dict = {'asc': 1, 'desc': -1}
 
class DataTablesServer:
 
    def __init__( self, request, columns, index, collection):
 
 
        self.columns = columns
        self.index = index
        self.collection = collection
         
        # values specified by the datatable for filtering, sorting, paging
        self.request_values = request.values
         
        # connection to your mongodb (see pymongo docs). this is defaulted to localhost
        self.dbh = MongoClient()
 
        # results from the db
        self.result_data = None
         
        # total in the table after filtering
        self.cardinality_filtered = 0
 
        # total in the table unfiltered
        self.cadinality = 0
 
        self.run_queries()
 
 
    def output_result(self):
        output = {}
        output['sEcho'] = str(int(self.request_values['sEcho']))
        output['iTotalRecords'] = str(self.cardinality)
        output['iTotalDisplayRecords'] = str(self.cardinality_filtered)
        aaData_rows = []
 
 
        for row in self.result_data:
            aaData_row = []
            for i in range( len(self.columns) ):
 
                aaData_row.append(row[ self.columns[i] ].replace('"','\\"'))
             
            # add additional rows here that are not represented in the database
            # aaData_row.append(('''<input id='%s' type='checkbox'></input>''' % (str(row[ self.index ]))).replace('\\', ''))
 
            aaData_rows.append(aaData_row)
 
        output['aaData'] = aaData_rows
 
        return output
 
    def run_queries(self):
 
        # 'mydb' is the actual name of your database
        mydb = self.dbh.mydb
 
        # pages has 'start' and 'length' attributes
        pages = self.paging()
         
        # the term you entered into the datatable search
        filter = self.filtering()
         
        # the document field you chose to sort
        sorting = self.sorting()
 
        # get result from db
        self.result_data = mydb[self.collection].find(spec = filter,
                                                      skip = pages.start,
                                                      limit = pages.length,
                                                      sort = sorting)
 
        total_count = len(list(mydb[self.collection].find(spec = filter)))
 
        self.result_data = list(self.result_data)
 
        self.cardinality_filtered = total_count
 
        self.cardinality = len(list( mydb[self.collection].find()))
 
    def filtering(self):
         
        # build your filter spec
        filter = {}
        if ( self.request_values.has_key('sSearch') ) and ( self.request_values['sSearch'] != "" ):
             
            # the term put into search is logically concatenated with 'or' between all columns
            or_filter_on_all_columns = []
             
            for i in range( len(self.columns) ):
                column_filter = {}
                column_filter[self.columns[i]] = {'$regex': self.request_values['sSearch'], '$options': 'i'}
                or_filter_on_all_columns.append(column_filter)
            filter['$or'] = or_filter_on_all_columns
        return filter
 
    def sorting(self):
        order = []
        # mongo translation for sorting order
         
        if ( self.request_values['iSortCol_0'] != "" ) and ( self.request_values['iSortingCols'] > 0 ):
            order = []
            for i in range( int(self.request_values['iSortingCols']) ):
                order.append((self.columns[ int(self.request_values['iSortCol_'+str(i)]) ], order_dict[self.request_values['sSortDir_'+str(i)]]))
        return order
 
    def paging(self):
        pages = namedtuple('pages', ['start', 'length'])
        if (self.request_values['iDisplayStart'] != "" ) and (self.request_values['iDisplayLength'] != -1 ):
            pages.start = int(self.request_values['iDisplayStart'])
            pages.length = int(self.request_values['iDisplayLength'])
        return pages
 
 
 
'''
$('#companies').dataTable( {
            "bProcessing": true,
            "bServerSide": true,
            "sPaginationType": "full_numbers",
            "bjQueryUI": true,
            "sAjaxSource": "/_retrieve_server_data"
});
 
'''
# create an app.route for your javascript. see above ^ for javascript implementation
@app.route("/_retrieve_server_data")
def get_server_data():
 
    columns = [ 'column_1', 'column_2', 'column_3', 'column_4']
    index_column = "_id"
    collection = "collection_name"
 
    results = DataTablesServer(request, columns, index_column, collection).output_result()
     
    # return the results as a string for the datatable
    return json.dumps(results)