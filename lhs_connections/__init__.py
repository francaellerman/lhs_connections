import flask
import logging
import pdfminer
import pickle
import datetime
import os
import lhs_connections.worker
import pathlib
import warnings
import pkg_resources
import pathlib
import logging_franca_link

wrapper_related = logging_franca_link.wrapper_related('franca_link.connections')
wrapper = wrapper_related.wrapper

app = flask.Blueprint('connections', __name__, template_folder='templates', static_folder='static')

start = 'connections/'

index_ = wrapper()
@app.route('/', methods=['GET'])
@index_
def index():
    user_agent = flask.request.headers.get('User-Agent').lower()
    if 'iphone' in user_agent or 'android' in user_agent: mobile = True
    else: mobile = False
    return flask.render_template('lhs_connections/index.html', mobile=mobile)

about_ = wrapper()
@app.route('/about', methods=['GET'])
@about_
def about():
    resp = flask.render_template('lhs_connections/about.html')
    return resp

@app.route('/api', methods=['POST'])
def post():
    information = {}
    resp = flask.make_response()
    file = None
    try:
        time = datetime.datetime.utcnow().isoformat()
        with warnings.catch_warnings(record=True) as caught_warnings:
            file = flask.request.files['pdf']
            md = worker.get_metadata(file)
            with pkg_resources.resource_stream('lhs_connections', 'pdf_metadata.pickle') as f:
                franca_md = pickle.load(f)
            if not (md['ModDate'] == md['CreationDate'] and
                    md['Creator'] == franca_md['Creator'] and
                    md['Producer'] == franca_md['Producer']):
                raise Exception("Metadata does not fit the criteria")
            if len(caught_warnings) > 0:
                raise Exception("Getting PDF metadata raised a warning")
        information = worker.get_pdf_info(file)
        if worker.returning_user_name(information['ID']):
            message = "Returning user POST"
        else:
            file.seek(0)
            worker.insert_sql_data(information, time, file)
            file.seek(0)
            file.save(os.path.join(start + "pdfs", f'{information["ID"]}_{time}.pdf'))
            message = "Request success"
        file.close()
    except:
        wrapper_related.exception(id_=information.get('ID'))
        #Could download file if something goes wrong
        flask.abort(500)
    else:
        wrapper_related.info(message, id_=information['ID'])
        flask.session['ID'] = information['ID']
    return resp

get_ = wrapper()
@app.route('/api', methods=['GET'])
@get_
def get():
    id_ = flask.session.get('ID')
    if not id_:
        r = 'No ID'
    else:
        name = worker.format_name(worker.returning_user_name(id_)[0][0])
        r = {'name': name,
            'class_list': worker.get_connections(id_)}
    resp = flask.json.jsonify(r)
    return resp

reset_ = wrapper()
@app.route('/reset', methods=['GET'])
@reset_
def reset():
    flask.session['ID'] = None
    return flask.make_response()
