class Calc():
	def rate(total, recycled):
		if total > 0:
			return "{0:.2f}".format(recycled / total * 100, 2)
		return 0	
