# Flask Database Manager

A dynamic Flask web application that provides a user-friendly interface for managing any PostgreSQL database. The application automatically detects database schema and generates CRUD (Create, Read, Update, Delete) operations for all tables.

## Features

- **Dynamic Schema Detection**: Automatically discovers and reflects database tables and columns
- **Full CRUD Operations**: Create, Read, Update, and Delete records from any table
- **Search Functionality**: Filter and search through database tables
- **Pagination**: Built-in pagination for large datasets
- **Schema Viewer**: View table structures and column types
- **User-Friendly Interface**: Web-based GUI for database operations
- **Flash Messages**: User feedback for successful operations and errors

## Prerequisites

- Python 3.7+
- PostgreSQL database
- Required Python packages (see requirements below)

## Installation

1. **Clone or download the application files**

2. **Install required dependencies**:
   ```bash
   pip install flask flask-sqlalchemy flask-paginate psycopg2-binary
   ```

3. **Create a credentials file** (`creds.py`):
   ```python
   # Database connection string
   pg_url = "postgresql://username:password@host:port/database_name"
   
   # Flask secret key for sessions
   flask_secret = "your-secret-key-here"
   ```

4. **Ensure your PostgreSQL database is accessible** and contains the tables you want to manage.

## Usage

### Starting the Application

```bash
python app.py
```

The application will start in debug mode and be available at `http://localhost:5000`

### Main Features

#### 1. Home Page (`/`)
- View all available database tables
- Search for specific tables using the search functionality
- Navigate to different operations

#### 2. Schema Viewer (`/read_schema`)
- View table structure and column information
- See column data types
- Access via: `http://localhost:5000/read_schema?table_name=your_table`

#### 3. Read Data (`/read`)
- View table contents with pagination
- Filter records by column values
- Navigate through pages of results
- Access via: `http://localhost:5000/read?table_name=your_table`

#### 4. Insert Data (`/insert`)
- Add new records to any table
- Form automatically generates based on table schema
- Provides success feedback
- Access via: `http://localhost:5000/insert?table_name=your_table`

#### 5. Update Data (`/update`)
- Modify existing records
- Pre-fills form with current values
- Update by primary key
- Access via: `http://localhost:5000/update?table_name=your_table&pk=primary_key_value`

#### 6. Delete Data (`/delete`)
- Remove records from tables
- Confirmation before deletion
- Delete by primary key
- Access via: `http://localhost:5000/delete?table_name=your_table&pk=primary_key_value`

## Project Structure

```
flask-db-manager/
├── app.py              # Main application file
├── creds.py           # Database credentials (create this)
├── templates/         # HTML templates (you'll need to create these)
│   ├── index.html
│   ├── read_schema.html
│   ├── read.html
│   ├── insert.html
│   ├── update.html
│   └── delete.html
└── README.md
```

## Required Templates

You'll need to create the following HTML templates in a `templates/` directory:

- `index.html` - Home page showing available tables
- `read_schema.html` - Display table schema information
- `read.html` - Display table data with pagination
- `insert.html` - Form for inserting new records
- `update.html` - Form for updating existing records
- `delete.html` - Confirmation page for deletions

## Configuration

### Database Connection
Update `creds.py` with your PostgreSQL connection details:

```python
pg_url = "postgresql://username:password@localhost:5432/your_database"
flask_secret = "your-secret-key-for-sessions"
```

### Pagination Settings
Default pagination is set to 10 records per page. You can modify this in the URL:
```
http://localhost:5000/read?table_name=your_table&per_page=20
```

## Security Considerations

- **Credentials**: Never commit `creds.py` to version control
- **Input Validation**: The application uses SQLAlchemy ORM which provides some protection against SQL injection
- **Access Control**: This application doesn't include authentication - consider adding it for production use
- **Network Security**: Run behind a reverse proxy in production

## Limitations

- Only works with tables that have primary keys
- Limited to PostgreSQL databases
- No built-in authentication or authorization
- No support for complex relationships or foreign key constraints in the UI

## Troubleshooting

### Common Issues

1. **"Invalid table name" error**
   - Ensure the table exists in your database
   - Check that the table has a primary key

2. **Database connection errors**
   - Verify your connection string in `creds.py`
   - Ensure PostgreSQL server is running
   - Check firewall and network connectivity

3. **Missing templates**
   - Create the required HTML templates in the `templates/` directory
   - Ensure template names match those referenced in the routes

### Debug Mode

The application runs in debug mode by default. For production:

```python
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

## License

This project is open source. Please check with your organization's policies before using in production environments.
