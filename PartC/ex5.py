import yaml
with open("config/tests.yaml") as f:
	data = yaml.safe_load(f)
print(data)
