import json
import argparse
import os

def convert_to_ublock(data):
  output_data = []
  # the ublock format is: website_name##+js(cookie-remover.js, cookie_name)

  for website in data:
    for cookie in data[website]:
      output_data.append(website + "##+js(cookie-remover.js, " + cookie + ")")
  
  return output_data

if __name__ == "__main__":
  # Take the input file (-i) and output file (-o) as arguments
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--input", help="Input file")
  parser.add_argument("-o", "--output", help="Output file")

  args = parser.parse_args()

  # Read the input file
  with open (args.input, "r") as f:
    data = json.load(f)
  

  # Convert the data to the ublock format
  output_data = convert_to_ublock(data)

  # Write the output to the output file
  with open (args.output, "w") as f:
    f.write(f"{os.linesep}".join(output_data))