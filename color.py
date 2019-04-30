import os

def c(color):
	if os.name == "nt":
		return ""
	else:
		if color == "red":
			return "\033[31m"
		elif color == "green":
			return "\033[32m"
		elif color == "yellow":
			return "\033[33m"
		elif color == "blue":
			return "\033[34m"
		elif color == "purple":
			return "\033[35m"
		elif color == "cian":
			return "\033[36m"
		elif color == "bold":
			return "\033[1m"
		elif color == "highlighted":
			return "\033[7m"
		elif color == "underline":
			return "\033[4m"
		else:
			return "\033[0m"
