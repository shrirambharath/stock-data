import argparse, datetime, os, json


def pick_assets(data_dir, last_date):
	selected_assets = { }

	for subdir in ['stocks','etfs']:
		dirpath = '%s/%s' % (data_dir, subdir)
		for file in os.listdir(dirpath):
			print ('Reading %s/%s' % (dirpath, file))

			with open('%s/%s' % (dirpath, file), 'r') as f:
				#reverse ordered lines
				lines = [l.strip() for l in f.read().split('\n') if len(l.strip()) > 0]
				lines.reverse()

				#extract date of the last line
				date = lines[0].split(',')[0]
				if date == last_date:
					asset = file.split('.')[0]
					selected_assets[asset] = { 'asset_type': subdir, 'filepath': '%s/%s' % (dirpath, file)}

	with open('%s/selected_assets.txt' % (data_dir), 'w') as f:
		f.write(json.dumps(selected_assets))

	return selected_assets



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', dest='data_dir', required=True, help="Directory to find the files stock/etf data directories")
	parser.add_argument('-l', default='2020-04-01', dest='last_date', required=False, help="Last date of asset data expected (yyyy-MM-dd")
	args = parser.parse_args()

	data_dir = args.data_dir
	last_date = args.last_date
	print('Picked Dir: %s' % data_dir)
	print('Picked Last Date: %s' % (last_date))
	
	selected_assets = pick_assets(data_dir, last_date)

main()
