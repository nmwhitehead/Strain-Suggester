from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import sys
from scipy import sparse
from spellchecker import SpellChecker
from sklearn.metrics.pairwise import pairwise_distances

strain_frame = pd.read_csv('../Data/Strain_Frame.csv')



app = Flask('Strain Suggester')

# main page
@app.route('/form')

def form():

    return render_template('form.html')

# response page
@app.route('/submit')

def submit():

    user_input = request.args
    strain = user_input['Strain']

    sys.stdout.flush()
    data = str(strain)


    pivot = strain_frame.pivot_table(index='Strain')
    pivot_sparse = sparse.csr_matrix(pivot.fillna(0))
    recommender = 100 - (pairwise_distances(pivot_sparse, metric='cosine') * 100)
    recommender_df = pd.DataFrame(recommender, index=pivot.index, columns=pivot.index)

    sc = SpellChecker(local_dictionary='../Data/Strain_List.json')

    def suggestion(data):
        strain_title = strain.title()
        try:
            print (f"Strains similar to {data.upper()} include ")
            suggestions = pd.DataFrame(recommender_df[strain_title].sort_values(ascending=False)[1:11]).round(decimals=2)
            suggestions = suggestions.to_html()
            return suggestions
        except:
            if sc.correction(strain) != data:
                return (f'Not Found. Did you mean {sc.correction(data)}?')
            else:
                return( '''Strain Not Found.
            If you searched the full strain name, try just the initials.''')

    output = suggestion(data)

    return render_template('suggestions.html', user_input=data, output=output)

if __name__ == '__main__':
    app.run(debug=True)
