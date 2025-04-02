# FoodieSpot-Agent

**FoodieSpot-Agent** is an AI-powered restaurant assistant built using Python and Streamlit. It helps users find restaurant recommendations based on city and cuisine preferences and allows them to make reservations seamlessly. The project leverages the CrewAI framework for agent-based workflows, integrates with a PostgreSQL database, and uses the Groq API for intent extraction.

## Features
- **Restaurant Recommendations**: Get personalized restaurant suggestions by city and cuisine.
- **Reservations**: Check table availability and book a table at your chosen restaurant.
- **Interactive UI**: Powered by Streamlit for a user-friendly chat interface.
- **Database Integration**: Stores restaurant and reservation data in a PostgreSQL database.
- **Agent-Based Workflow**: Uses CrewAI agents for intent detection, recommendations, and reservations.

## Project Structure

Below is the file organization of the project:
```
FOODIESPOT-AGENT/
├── .pytest_cache/              # Cache for pytest
├── agents/                     # Agent modules for different functionalities
│   ├── init.py
│   ├── chat.py                # Handles intent extraction and chat logic
│   ├── database.py            # Manages database interactions
│   ├── recommendation.py      # Provides restaurant recommendations
│   ├── reservation.py         # Handles reservation logic
├── database/                   # Database-related files or modules
│   ├── init.py
│   └── connect.py             # Database connection logic (example)
│   └── queries.py             # SQL queries for database operations
├── frontend/                   # Frontend application
│   ├── init.py
│   └── app.py                # Streamlit app for the user interface
├── logs/                       # Log files
│   ├── crew_logs.log         # Logs for crew activities
│   └── logger.py             # Logging configuration
├── tests/                      # Test suite
│   ├── init.py
│   ├── test_agents.py        # Tests for agent modules
│   ├── test_db.py            # Tests for database operations
│   └── test_logger.py        # Tests for logging functionality
├── venv/                       # Virtual environment
├── .env                        # Environment variables (not tracked in Git)
├── .gitignore                  # Git ignore file
├── main.py                     # Entry point for running the app
├── README.md                   # Project documentation (this file)
└── requirements.txt            # Python dependencies
```

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **PostgreSQL**: A running PostgreSQL server for the database.
- **Groq API Key**: Required for intent extraction via the Groq API.
- **Virtual Environment**: Recommended to manage dependencies.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/foodiespot-agent.git
cd foodiespot-agent
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up the Database
- Install PostgreSQL if not already installed.
- Create a database named foodiespot:
```bash
psql -U postgres
CREATE DATABASE foodiespot;
\q
```
- Create the necessary tables (see Database Schema below). You can copy the SQL commands provided in that section into a file (e.g., schema.sql) and apply it:
```bash
psql -U postgres -d foodiespot -f schema.sql
```
Alternatively, you can manually run the SQL commands in psql to set up the tables.

### 5. Configure Environment Variables
Create a .env file in the project root and add the following variables:
```env
GROQ_API_KEY=<your-groq-api-key>
DB_NAME=foodiespot
DB_USER=<your-username>
DB_PASSWORD=<your-password>
DB_HOST=localhost
DB_PORT=5432
```
- Note: Replace <your-groq-api-key> with your actual Groq API key.
- Note: Replace <your-username> with your actual PostgreSQL username.
- Note: Replace <your-password> with your actual PostgreSQL password.

### 6. Run the Application
Start the Streamlit app:
```bash
streamlit run frontend/app.py
```

## Usage:
### 1. Get Recommendations:
- Type a query like "places to eat in Mumbai" to get restaurant recommendations.
- The app will display a list of restaurants.
- You can also mention cuisines to get refined results
### 2. Make a Reservation:
- Type "make a reservation at <restaurant-name>" (e.g., "make a reservation at Taj Mahal Restaurant").
- Fill in the reservation form with the restaurant name, date, time, and number of people.
- Check availability and confirm the booking with your name and contact details.

## Environment Variables
The `.env` file contains the following configurations:

| Variable         | Description                          
|------------------|--------------------------------------
| `GROQ_API_KEY`   | API key for Groq API access         
| `DB_NAME`        | PostgreSQL database name            
| `DB_USER`        | PostgreSQL username                 
| `DB_PASSWORD`    | PostgreSQL password                 
| `DB_HOST`        | PostgreSQL host                     
| `DB_PORT`        | PostgreSQL port                     

## Database Schema
The application uses a PostgreSQL database named `foodiespot` with three main tables: `restaurants`, `tables`, and `reservations`. Below are the schema details for each table.

### `restaurants` Table
Stores information about restaurants.

| Column         | Type          | Constraints       | Default                     | Description                   |
|----------------|---------------|-------------------|-----------------------------|-------------------------------|
| `id`           | `integer`     | `PRIMARY KEY`     | `nextval('restaurants_id_seq')` | Unique restaurant ID          |
| `name`         | `varchar(255)`| `NOT NULL`        |                             | Restaurant name               |
| `location`     | `varchar(255)`| `NOT NULL`        |                             | Restaurant location (city)    |
| `cuisine`      | `varchar(100)`|                   |                             | Cuisine type                  |
| `contact`      | `varchar(50)` |                   |                             | Contact information           |
| `opening_time` | `time`        |                   |                             | Opening time                  |
| `closing_time` | `time`        |                   |                             | Closing time                  |

- **Indexes**: `restaurants_pkey` (btree on `id`)
- **Referenced By**:
  - `reservations` (via `restaurant_id`)
  - `tables` (via `restaurant_id`)

### `tables` Table
Stores information about tables in each restaurant.

| Column            | Type          | Constraints       | Default                 | Description                   |
|-------------------|---------------|-------------------|-------------------------|-------------------------------|
| `id`              | `integer`     | `PRIMARY KEY`     | `nextval('tables_id_seq')` | Unique table ID               |
| `restaurant_id`   | `integer`     |                   |                         | References `restaurants(id)`  |
| `seating_capacity`| `integer`     | `NOT NULL`        |                         | Number of people the table can seat |
| `is_available`    | `boolean`     |                   | `true`                 | Availability status           |
| `last_updated`    | `timestamp`   |                   | `CURRENT_TIMESTAMP`    | Last update timestamp         |

- **Indexes**: `tables_pkey` (btree on `id`)
- **Foreign Key**: `tables_restaurant_id_fkey` (`restaurant_id` references `restaurants(id)` with `ON DELETE CASCADE`)
- **Referenced By**: `reservations` (via `table_id`)
- **Triggers**: `table_update_trigger` (executes `notify_table_update()` after updates)

### `reservations` Table
Stores reservation details.

| Column            | Type          | Constraints       | Default                 | Description                   |
|-------------------|---------------|-------------------|-------------------------|-------------------------------|
| `id`              | `integer`     | `PRIMARY KEY`     | `nextval('reservations_id_seq')` | Unique reservation ID         |
| `restaurant_id`   | `integer`     |                   |                         | References `restaurants(id)`  |
| `table_id`        | `integer`     |                   |                         | References `tables(id)`       |
| `customer_name`   | `varchar(255)`|                   |                         | Name of the customer          |
| `customer_contact`| `varchar(50)` |                   |                         | Customer contact info         |
| `reservation_time`| `timestamp`   |                   |                         | Time of the reservation       |
| `status`          | `varchar(20)` | `CHECK`           |                         | Status (`confirmed`, `pending`, `cancelled`) |
| `created_at`      | `timestamp`   |                   | `CURRENT_TIMESTAMP`    | Creation timestamp            |
| `num_people`      | `integer`     |                   | `1`                    | Number of people in the party |

- **Indexes**: `reservations_pkey` (btree on `id`)
- **Check Constraint**: `reservations_status_check` (ensures `status` is one of `confirmed`, `pending`, `cancelled`)
- **Foreign Keys**:
  - `reservations_restaurant_id_fkey` (`restaurant_id` references `restaurants(id)` with `ON DELETE CASCADE`)
  - `reservations_table_id_fkey` (`table_id` references `tables(id)` with `ON DELETE CASCADE`)


### SQL to Create Tables
You can use the following SQL commands to create the tables in your foodiespot database. Save this as schema.sql and apply it as described in the setup instructions.
```sql
-- Create restaurants table
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    cuisine VARCHAR(100),
    contact VARCHAR(50),
    opening_time TIME,
    closing_time TIME
);

-- Create tables table
CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    seating_capacity INTEGER NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reservations table
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id) ON DELETE CASCADE,
    table_id INTEGER REFERENCES tables(id) ON DELETE CASCADE,
    customer_name VARCHAR(255),
    customer_contact VARCHAR(50),
    reservation_time TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('confirmed', 'pending', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    num_people INTEGER DEFAULT 1
);
```


## File Descriptions
- agents/chat.py: Extracts user intent (e.g., "restaurants" or "reservation") using the Groq API and processes user input.
- agents/database.py: Handles database connections and operations with PostgreSQL.
- agents/recommendation.py: Fetches restaurant recommendations based on city and cuisine.
- agents/reservation.py: Manages table availability checks and reservations.
- agents/queries.py: Contains SQL queries for database operations.
- frontend/app.py: The main Streamlit app for the user interface.
- logs/crew_logs.log: Logs agent activities for debugging.
- logs/logger.py: Configures logging for the application.
- tests/: Unit tests for agents, database, and logging.
- main.py: Alternative entry point to run the app (if not using Streamlit directly).


## Testing
Run the test suite using pytest:
```bash
pytest tests/
```


### Contributing
1. Fork the repository.
2. Create a feature branch (git checkout -b feature/YourFeature).
3. Commit your changes (git commit -m "Add YourFeature").
4. Push to the branch (git push origin feature/YourFeature).
5. Open a Pull Request.


## Acknowledgments
- Built with [Streamlit](https://streamlit.io/) for the frontend.
- Uses [CrewAI](https://github.com/joaomdmoura/crewAI) for agent workflows.
- Integrates with [PostgreSQL](https://www.postgresql.org/) for data storage.
- Powered by [Groq API](https://console.groq.com/playground) for intent extraction.

## Contributors
This project was made possible by the following contributors:
- [Praneesh Sharma](https://github.com/Praneesh-Sharma)
- [Nayeer Naushad](https://github.com/nayeer1169)
- [Preenon Saha](https://github.com/Preenon1462003)
- [Shibaa Naik](https://github.com/shibaanaik)
- [Shravan Sererl](https://github.com/shravan-serel)
- [Rishav Das](https://github.com/Rishavdas07)