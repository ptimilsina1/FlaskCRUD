from flask import Flask, render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, inspect, Table
from sqlalchemy import and_, Column, Integer
from flask_paginate import Pagination, get_page_parameter
import creds as cr


from flask import Flask, render_template, request,redirect, url_for

pg_url = cr.pg_url
engine = create_engine(pg_url)
metadata = MetaData()
metadata.reflect(bind=engine)

app = Flask(__name__)
app.config['SECRET_KEY'] = cr.flask_secret
app.config['TEMPLATES_AUTO_RELOAD']
app.jinja_env.globals.update(zip=zip)
app.config['SQLALCHEMY_DATABASE_URI'] = pg_url
db = SQLAlchemy(app)


models = {}
for table_name in metadata.tables:
    table = metadata.tables[table_name]
    if len(table.primary_key.columns) > 0:
        model = type(table_name.title().replace('_', ''), (db.Model,), {'__table__': table})
        models[table_name] = model



@app.route('/')
def index():
    search = request.args.get('search')
    tables = list(models.keys())
    if search:
        tables = [t for t in tables if search.lower() in t.lower()]
    tables.sort()
    return render_template('index.html', tables=tables, search=search)


@app.route('/read_schema', methods=['GET'])
def read_schema():
    table_name = request.args.get('table_name')
    model_class = models.get(table_name)
    if model_class is None:
        return 'Error: Invalid table name'
    columns = model_class.__table__.columns.keys()
    column_types = [column.type for column in table.columns]
    return render_template('read_schema.html', table_name=table_name, columns=columns,column_types =column_types)
@app.route('/read', methods=['GET', 'POST'])
def read_data():
    tables = list(metadata.tables.keys())
    if request.method == 'POST':
        table_name = request.form['table_name']
        model_class = models.get(table_name)
        if model_class:
            filter_args = {}
            for column in model_class.__table__.columns:
                if column.name in request.form:
                    filter_args[column.name] = request.form[column.name]
            if filter_args:
                filter_expr = and_(*(getattr(model_class, col) == val for col, val in filter_args.items()))
                query = model_class.query.filter(filter_expr)
            else:
                query = model_class.query
        else:
            query = None
    else:
        table_name = request.args.get('table_name', tables[0])
        model_class = models.get(table_name)
        if model_class is None:
            return 'Error: Invalid table name'
        query = model_class.query
        filter_args = {}
        for column in model_class.__table__.columns:
            if column.name in request.args:
                filter_args[column.name] = request.args[column.name]
        if filter_args:
            filter_expr = and_(*(getattr(model_class, col) == val for col, val in filter_args.items()))
            query = query.filter(filter_expr)
            # check if filtered primary key exists in the database
            pk_values = [filter_args.get(pk_column) for pk_column in model_class.__table__.primary_key.columns.keys()]
            model = model_class.query.get(pk_values)
            if model is None:
                flash('Item does not exist', 'error')
                return redirect(url_for('read_data', table_name=table_name))
    if query:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        pagination = query.paginate(page=page, per_page=per_page)
        data = pagination.items
        pk_column = model_class.__table__.primary_key.columns.keys()[0]
        return render_template('read.html', data=data, table_name=table_name, tables=tables, pk_column=pk_column,
                               getattr=getattr, pagination=pagination)
    else:
        return 'Error: Invalid table name'

    

@app.route('/insert', methods=['GET', 'POST'])
def insert_data():
    tables = list(metadata.tables.keys())
    if request.method == 'POST':
        table_name = request.form['table_name']
        table_columns = metadata.tables[table_name].columns.keys()
        data = {column: request.form[column] for column in table_columns}
        table = metadata.tables[table_name]
        insert_stmt = table.insert().values(data)
        db.session.execute(insert_stmt)
        db.session.commit()

        flash('Data successfully inserted!', 'success')
        return f'''<script>
                        alert('Data successfully inserted!');
                        window.location.href = "{url_for('read_data', table_name=table_name)}";
                    </script>'''

    table_name = request.args.get('table_name')
    if table_name:
        model_class = models.get(table_name)
        if model_class:
            model_columns = [column.name for column in model_class.__table__.columns]
    else:
        model_columns = metadata.tables[tables[0]].columns.keys()
    return render_template('insert.html', tables=tables, model_columns=model_columns, table_name=table_name)

@app.route('/update', methods=['GET', 'POST'])
def update_data():
    tables = list(metadata.tables.keys())
    model_class = None
    model = None
    pk_column = None
    if request.method == 'POST':
        # handle form submission
        table_name = request.form['table_name']
        model_class = models.get(table_name)
        if model_class:
            pk = request.form.get('pk')
            if pk:
                model = model_class.query.get(pk)
                if model:
                    for field in model_class.__table__.columns:
                        if field.name != pk_column:
                            value = request.form.get(field.name)
                            if value is not None:
                                setattr(model, field.name, value)
                    db.session.commit()
                    return redirect(url_for('read_data', table_name=table_name))
                else:
                    return f'Error: No data found for {pk_column}={pk}'
            else:
                return f'Error: Invalid {pk_column}'
    else:
        # handle GET request to display form
        table_name = request.args.get('table_name', tables[0])
        model_class = models.get(table_name)
        if model_class is None:
            return 'Error: Invalid table name'
        pk_column = model_class.__table__.primary_key.columns.keys()[0]
        pk_value = request.args.get('pk')
        if pk_value:
            model = model_class.query.get(pk_value)
    return render_template('update.html', tables=tables, pk_column=pk_column, table_name=table_name,
                            model_class=model_class, getattr=getattr, model=model,pk_value=pk_value)

@app.route('/delete', methods=['GET', 'POST'])
def delete_data():
    tables = list(metadata.tables.keys())
    model_class = None
    pk_column = None
    if request.method == 'POST':
        table_name = request.form['table_name']
        model_class = models.get(table_name)
        if model_class:
            pk = request.form.get('pk')
            if pk:
                model = model_class.query.get(pk)
                if model:
                    db.session.delete(model)
                    db.session.commit()
                    flash('Data deleted successfully', 'success')
                else:
                    flash(f'Error: No data found for {pk_column}={pk}', 'error')
            else:
                flash(f'Error: Invalid {pk_column}', 'error')
        return redirect(url_for('read_data', table_name=table_name))
    else:
        table_name = request.args.get('table_name', tables[0])
        model_class = models.get(table_name)
        if model_class is None:
            return 'Error: Invalid table name'
        pk_column = model_class.__table__.primary_key.columns.keys()[0]
        pk_value = request.args.get('pk')
        if pk_value:
            model = model_class.query.get(pk_value)
    return render_template('delete.html', tables=tables, pk_column=pk_column, table_name=table_name, pk_value=pk_value)

if __name__ == "__main__":
    app.run(debug=True)

