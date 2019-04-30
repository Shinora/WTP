import os

def c(color):
	if os.name == "nt":
		return ""
	if color == "red":
		return "\033[31m"
	if color == "green":
		return "\033[32m"
	if color == "yellow":
		return "\033[33m"
	if color == "blue":
		return "\033[34m"
	if color == "purple":
		return "\033[35m"
	if color == "cian":
		return "\033[36m"
	if color == "bold":
		return "\033[1m"
	if color == "highlighted":
		return "\033[7m"
	if color == "underline":
		return "\033[4m"
	return "\033[0m"
