# Technical Glossary Web Scraper

An efficient and robust web scraper designed to extract technical terms and their definitions from tugurium.com website, organizing them into CSV files for easy consultation and analysis.

## 🚀 Features

- **Concurrent scraping**: Parallel processing of multiple terms for enhanced efficiency
- **Incremental saving**: Prevents data loss by saving progress at regular intervals
- **Robust error handling**: Retry system with exponential backoff
- **Smart filtering**: Avoids processing already extracted terms
- **Rate limiting**: Random pauses to simulate human behavior

## 📋 Requirements

- Python 3.7+
- Internet connection

## 🔧 Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd script-web
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4 pandas
```

## 🎯 Usage

### Basic usage

Run the script to extract terms starting with letter "D":

```bash
python script.py
```

### Customization

You can modify the following variables in the script:

- **Target URL**: Change the `url` variable to extract terms from different letters
- **Output file**: Modify `nombre_archivo` to change the CSV file name
- **Batch size**: Adjust `batch_size` to change saving frequency
- **Number of workers**: Modify `max_workers` in ThreadPoolExecutor to adjust concurrency

### Customization example:

```python
# To extract terms starting with "A"
url = 'http://www.tugurium.com/gti/contenido.php?INI=A'
nombre_archivo = 'glosario_letra_A.csv'

# To change batch size
scrapeo_progresivo(items, nombre_archivo, batch_size=50)
```

## 📊 Output data structure

The script generates a CSV file with the following columns:

| Column | Description |
|---------|-------------|
| Término | Technical term name |
| Descripciones | Brief description of the term |
| Información Adicional | Detailed definition extracted from the specific page |

## 🛠️ Project Architecture

### Main functions:

- `obtener_detalles()`: Extracts detailed information from individual pages
- `procesar_entrada()`: Processes each found term
- `leer_csv_existente()`: Reads existing CSV files to avoid duplicates
- `guardar_csv_incremental()`: Saves progress incrementally
- `scrapeo_progresivo()`: Controls the main scraping flow

### Technical features:

- **Concurrency**: Uses ThreadPoolExecutor with 5 workers by default
- **Error handling**: Automatic retries with exponential backoff
- **Custom headers**: User-Agent to avoid automatic restrictions
- **Rate limiting**: Random pauses between 1-3 seconds between requests

## ⚠️ Important Considerations

### Responsible usage
- The script includes pauses to avoid overloading the server
- Respects the target website's terms of service
- Use for educational and research purposes

### Performance
- Execution time depends on the number of terms to process
- Recommended to run the script during low traffic hours
- Consider increasing batch_size to reduce disk write frequency

## 🔍 Troubleshooting

### Common errors:

1. **Connection error**: Check your internet connection
2. **Timeout**: The website might be slow, the script will retry automatically
3. **CSV file locked**: Close any program that might be using the CSV file

### Logs and debugging:

The script provides detailed information during execution:
- Total number of new terms found
- Progress every 100 processed terms
- Total execution time
- Specific errors with retry details

## 📝 Future improvements

- [ ] Configuration via config file
- [ ] Support for multiple letters in single execution
- [ ] More robust command line interface
- [ ] Support for different output formats (JSON, XML)
- [ ] Web dashboard to monitor progress

## 🤝 Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is free to use for educational and research purposes. Use it responsibly and respect the target website's terms of service.

## 🙏 Acknowledgments

- Developed to extract information from tugurium.com technical glossary
- Uses excellent Python libraries: requests, BeautifulSoup4, and pandas