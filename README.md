# Book cover fetcher

Takes a list of ISBNs and queries the Google Books API to find thumbnail images of the books' covers.

## API Key

You need to provide an API key value in `config.py`. Either ask me for mine or create a project at https://console.developers.google.com/project and create a public API key (choose browser key).

## Usage

Use it via the command line.

```
usage: booker.py [-h] [-i ISBN_COLUMN] [-o OUTPUT_PATH] input_csv

positional arguments:
  input_csv             Path to the csv file containing ISBNs

optional arguments:
  -h, --help            show this help message and exit
  -i ISBN_COLUMN, --isbn-column ISBN_COLUMN
                        Name of column containing ISBNs. Defaults to 'isbn'
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        Where to write the thumbnails. Defaults to 'thumbs'
```

## Examples

### As basic as it gets.

    ./booker.py <csv_file>

### Specifying a different output path

    ./booker.py <csv_file> -o <new_output_path>

### Specifying a column containing ISBNs that isn't named `isbn`

    ./booker.py <csv_file> -i <name_of_isbn_column>

## Limits

The Google Books API caps requests to 1000 per day, and 1 per second. The script throttles to 1 per second, but if you might find that you're hitting the daily quota. If so you should see an error message printed out about daily quote being exceeded. In that case try again tomorrow and it should work.
