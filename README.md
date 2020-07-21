# stock-data

All the raw data was downloaded from here: https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs/discussion/134703

Step 1:
- Run 'python pick-assets.py -d <data_dir> -s <start_year>' (identifies the stocks/etfs to actually track that are currently traded in the stock market). Generates the file 'selected_assets.txt' in <data_dir>

Step 2:
- Run 'python prepare-annual-asset-data.py -d <data_dir> -y <start_date> -e <end_date>' to generate the lookahead change in price by day for each asset tracked. Data will get written into the directory '<data_dir>/lookahead_deltas/' as <year>.txt.gz. Re-running a specific year will overwrite the previous run.
	- The format of the <year>.txt.gz is: 
		<date> <asset> <closing_price> <1-week chg %> <4-week chg %> <12-week chg %> <24-week chg %>


