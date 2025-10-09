# Technical Glossary Web Scraper

I built this web scraper to extract technical terms and their definitions from tugurium.com. It's designed to be efficient and reliable, organizing the extracted data into CSV files that are easy to work with.

## Features

This scraper includes several features that I've found essential for reliable web scraping:

- **Concurrent processing**: The script processes multiple terms at once, which significantly speeds up the extraction process
- **Incremental saving**: One of the most frustrating things about scraping is losing progress when something goes wrong. This script saves data in batches, so you never lose everything
- **Smart error handling**: Web scraping can be unpredictable. I've implemented a retry system that handles temporary network issues gracefully
- **Duplicate prevention**: The script remembers what it has already scraped, so you can safely run it multiple times without duplicating work
- **Respectful rate limiting**: Random pauses between requests help avoid overwhelming the target server

## What You'll Need

- Python 3.7 or newer
- A stable internet connection

## Getting Started

Setting up the scraper is straightforward:

1. Clone or download this repository:
```bash
git clone <repository-url>
cd script-web
```

2. Install the required libraries:
```bash
pip install -r requirements.txt
```

If you prefer to install packages manually:
```bash
pip install requests beautifulsoup4 pandas
```

## How to Use It

### Basic Usage

To start scraping terms that begin with the letter "D":

```bash
python script.py
```

The script will create a CSV file called `glosario_letra_D.csv` with all the extracted terms.

### Customizing the Scraper

I've designed the script to be easily customizable. Here are the main things you can change:

- **Different letters**: Change the `url` variable to scrape terms starting with different letters
- **Output filename**: Modify `nombre_archivo` to save with a different name
- **Batch size**: Adjust `batch_size` if you want to save more or less frequently
- **Concurrency**: Change `max_workers` to use more or fewer threads

For example, to scrape terms starting with "A":

```python
# Change these variables in the script
url = 'http://www.tugurium.com/gti/contenido.php?INI=A'
nombre_archivo = 'glosario_letra_A.csv'
```

## Understanding the Output

The scraper creates a CSV file with three columns:

| Column | What it contains |
|---------|------------------|
| Término | The technical term itself |
| Descripciones | A brief description or definition |
| Información Adicional | Detailed information scraped from the term's individual page |

## How It Works Under the Hood

I've organized the code into several functions that each handle a specific part of the process:

- `obtener_detalles()`: This function visits individual term pages to get detailed definitions
- `procesar_entrada()`: Processes each term found on the main page
- `leer_csv_existente()`: Checks for existing CSV files to avoid re-scraping
- `guardar_csv_incremental()`: Handles the incremental saving functionality
- `scrapeo_progresivo()`: Orchestrates the entire scraping process

### Technical Details

The scraper uses several techniques to be reliable and respectful:

- **ThreadPoolExecutor**: Allows processing multiple terms simultaneously (I use 5 threads by default)
- **Exponential backoff**: When requests fail, the script waits progressively longer between retries
- **Custom headers**: Includes a realistic User-Agent string to avoid automatic blocking
- **Random delays**: Pauses 1-3 seconds between requests to simulate human browsing

## Important Notes

### Using This Responsibly

I've built in several features to ensure the scraper is respectful:

- Automatic delays prevent overwhelming the server
- The script follows reasonable rate limits
- It's designed for educational and research purposes

Please use this tool responsibly and respect the website's terms of service.

### Performance Considerations

A few things to keep in mind:

- Execution time depends on how many terms need to be processed
- Running during off-peak hours is more considerate and often faster
- Increasing the batch size reduces how often the script writes to disk
- The concurrent processing significantly speeds up the overall process

## When Things Go Wrong

### Common Issues

From my experience, these are the most common problems you might encounter:

1. **Connection errors**: Usually temporary network issues. The script will retry automatically.
2. **Timeouts**: Sometimes the website is slow to respond. The retry mechanism handles this.
3. **File access errors**: Make sure no other programs have the CSV file open when running the script.

### Monitoring Progress

The script provides detailed feedback while running:

- Shows the total number of new terms found
- Reports progress every 100 terms processed
- Displays execution time and processing statistics
- Logs any errors with details about retry attempts

## Future Improvements

I have several ideas for enhancing this scraper:

- Adding configuration file support for easier customization
- Supporting multiple letters in a single run
- Creating a more sophisticated command-line interface
- Adding support for different output formats like JSON or XML
- Building a simple web interface to monitor progress

## Contributing

If you'd like to improve this scraper, I'd welcome your contributions:

1. Fork the repository
2. Create a feature branch with a descriptive name
3. Make your changes and test them thoroughly
4. Write clear commit messages
5. Submit a pull request with a description of what you've changed

## License and Usage

This project is freely available for educational and research purposes. I ask that you use it responsibly and respect the terms of service of any websites you scrape.

## Acknowledgments

This scraper was developed specifically for extracting information from the tugurium.com technical glossary. It relies on some excellent Python libraries that make web scraping much more manageable: requests for HTTP handling, BeautifulSoup4 for HTML parsing, and pandas for data manipulation.