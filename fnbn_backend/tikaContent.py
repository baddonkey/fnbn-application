from tika import parser

class TikaContent():

	def __init__(self):
		pass

	def extract_content(self, filename):
		return parser.from_file(filename, service="meta")

