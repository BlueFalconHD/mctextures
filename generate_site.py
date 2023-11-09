# Import necessary libraries
import json
from jinja2 import Environment, FileSystemLoader

# The script will use the Jinja2 templating engine to render the HTML

# Define the path to the templates
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

# Define the template file we will use
template = env.get_template('index.html')

# Read the json file
with open('./textures.json', 'r') as file:
    textures_data = json.load(file)

# Render the template with the textures data
output_html = template.render(categories=textures_data)

# Write the output to an HTML file
with open('index.html', 'w') as file:
    file.write(output_html)

print("Website generated successfully!")
