# Price vs Score on LLM Thai O-NET Graph

![LLM Thai O-NET Graph](/screen_shot_page.png)

A data visualization web application that compares LLM (Large Language Model) performance on Thai O-NET exams against their cost. This project analyzes how different AI models perform on Thai educational assessments and visualizes the price-performance relationship.

## Special Thanks

Thank you to [AI vs Thai Exams](https://ai-vs-thai-exams.pages.dev/) for providing the data used in this project, all the praises should go there.

## Overview

This project fetches data from an external repository containing LLM performance results on Thai O-NET exams, processes the data, and displays it in an interactive web application built with Astro. The visualization includes a scatter plot showing the relationship between model accuracy and cost, with a Pareto frontier line highlighting the most efficient models.

## Setup and Usage

### Prerequisites

- Node.js and npm/bun
- Python 3.x
- Git

### Step 1: Setup Data Source

Run the `update_source.sh` script to fetch the necessary data files from the external repository:

```bash
./update_source.sh
```

This script will:
- Add a remote repository if it doesn't exist
- Fetch the latest data using sparse checkout
- Extract the required files to the `external/` directory

### Step 2: Prepare Database

Run the Python script to process the data and create a DuckDB database:

```bash
python prepare_db.py
```

This script will:
- Decompress the snapshot file
- Convert JSONL data to a DuckDB database
- Process question data from various test files
- Add model price and icon information to the database

### Step 3: Run the Web Application

Start the development server using Bun:

```bash
bun run dev
```

Or build for production:

```bash
bun run build
```

## Project Structure

- `update_source.sh`: Script to fetch data from external repository
- `prepare_db.py`: Script to process data and create DuckDB database
- `src/`: Source code for the Astro web application
  - `pages/`: Astro page components
  - `components/`: Reusable UI components
  - `layouts/`: Page layout templates
- `external/`: Directory for external data files (created by scripts)
- `model_price_icon.csv`: Data about model pricing and icons

## Features

- Interactive scatter plot of LLM performance vs. cost
- Pareto frontier visualization showing optimal price-performance models
- Sortable data table with model details
- Toggle between logarithmic and linear scales
- Option to show/hide model labels

## Data Sources

The data comes from the [LLM Performance on Thai O-NET Tests](https://ai-vs-thai-exams.pages.dev/onet_m6) project, which evaluates various language models on Thai educational assessments.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
