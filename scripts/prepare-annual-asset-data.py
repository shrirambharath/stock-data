import argparse, datetime, json
import tempfile, os, gzip

IN_MEMORY_DATE_LOOKBACK_WEEKS = 1
IN_MEMORY_DATE_LOOKAHEAD_WEEKS = 26

class AssetFileReader:
	def __init__(self, filename):
		self.filename = filename
		self.file_handle = open(filename, 'r')
		self.line_num = 0

		self.in_memory_data = { }


	def seek(self, date):
		if len(self.in_memory_data) > 0 :
			min_date = min(self.in_memory_data.keys())
			while min_date < (date - datetime.timedelta(weeks = IN_MEMORY_DATE_LOOKBACK_WEEKS)):
				del self.in_memory_data[min_date]
				min_date = min(self.in_memory_data.keys())

		for line in self.file_handle:
			self.line_num += 1 
			if self.line_num == 1:
				continue

			if self.line_num % 2000 == 0:
				print('Read %d line from file %s' % (self.line_num, self.filename))

			cols = [x.strip() for x in line.split(',')]
			line_date = datetime.datetime.strptime(cols[0], '%Y-%m-%d').date()
			if line_date < (date - datetime.timedelta(weeks = IN_MEMORY_DATE_LOOKBACK_WEEKS)):
				continue

			try:
				adj_close = float(cols[5])
				volumne = float(cols[6])
				self.in_memory_data[line_date] = (adj_close, volumne)
			except ValueError as e:
				continue

			if line_date >= (date + datetime.timedelta(weeks = IN_MEMORY_DATE_LOOKAHEAD_WEEKS)):
				break

	def close(self):
		self.file_handle.close()

	def _retrieve_date_information(self, d):
		if d < min(self.in_memory_data.keys()):
			return (0.0, 0.0)

		if d in self.in_memory_data:
			(adj_close, volume) = self.in_memory_data[d]
		else:
			#may be a holiday. use the closing price of the last prior open day
			d = d - datetime.timedelta(days = 1)
			while d not in self.in_memory_data:
				#market cannot stay closed for over 3 consecutive calendar days
				d = d - datetime.timedelta(days = 1)
			(adj_close, volume) = self.in_memory_data[d]
		return (adj_close, volume)


	def aggregate(self, date):
		(curr_adj_close, curr_volume) = self._retrieve_date_information(date)

		#n-wk deltas
		delta_map = { }
		delta_map[0] = curr_adj_close #current price
		for delta_margin_weeks in [1, 4, 12, 24]:
			d = date + datetime.timedelta(days = 7 * delta_margin_weeks)
			(adj_close, _) = self._retrieve_date_information(d)
			try:
				closing_price_delta = (adj_close - curr_adj_close) / curr_adj_close
			except:
				closing_price_delta = 0.0
			delta_map[delta_margin_weeks] = closing_price_delta

		return ['%.5f' % (delta_map[x]) for x in sorted(delta_map.keys())]


def retrieve_tracked_assets(data_dir):
	filename = '%s/selected_assets.txt' % (data_dir)
	with open(filename, 'r') as f:
		selected_assets = json.loads(f.read())
	return selected_assets


def prepare_output_handle(data_dir, year):
	_dir_path = '%s/lookahead_deltas' % data_dir
	try:
		os.mkdir(_dir_path)
	except FileExistsError as e:
		pass

	_file_path = '%s/lookahead_deltas/%d.txt.gz' % (data_dir, year)
	try:
		os.remove(_file_path)
	except FileNotFoundError as e:
		pass

	return gzip.open(_file_path,'wb')


def process_data(data_dir, start_date, end_date, selected_assets):
	asset_readers = { }
	for asset in sorted(selected_assets.keys()):
		asset_details = selected_assets[asset]
		asset_readers[asset] = AssetFileReader(asset_details['filepath'])


	d = start_date
	curr_year = d.year
	out = prepare_output_handle(data_dir, curr_year)

	while d <= end_date:
		for asset in sorted(asset_readers.keys()):
			asset_readers[asset].seek(d)
			aggs = asset_readers[asset].aggregate(d)

			cols = [str(d), asset] + aggs
			line = ('%s\n' % ('\t'.join(cols))).encode('utf-8')
			out.write(line)

		d += datetime.timedelta(days = 1)
		new_year = d.year
		if curr_year != new_year:
			out.close()
			out = prepare_output_handle(data_dir, new_year)
			curr_year = new_year

	out.close()




def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', dest='data_dir', required=True, help="Directory to find the files stock/etf data directories")
	parser.add_argument('-s', default='2000-01-01', dest='first_date', required=True, help="First date of asset data lookahead aggs")
	parser.add_argument('-e', default='2020-03-31', dest='last_date', required=True, help="Last date of asset data lookahead aggs")
	args = parser.parse_args()

	data_dir = args.data_dir
	start_date = datetime.datetime.strptime(args.first_date, '%Y-%m-%d').date()
	last_date = datetime.datetime.strptime(args.last_date, '%Y-%m-%d').date()
	print('Picked Dir: %s' % data_dir)
	print('Picked First Date:', start_date)
	print('Picked Last Date:', last_date)

	selected_assets = retrieve_tracked_assets(data_dir)
	process_data(data_dir, start_date, last_date, selected_assets)

main()


