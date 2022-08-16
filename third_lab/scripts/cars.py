#!/usr/bin/env python3

import json
import locale
import sys
import emails
import os
import reports

def load_data(filename):
  """Loads the contents of filename as a JSON file."""
  with open(filename) as json_file:
    data = json.load(json_file)
  return data


def format_car(car):
  """Given a car dictionary, returns a nicely formatted name."""
  return "{} {} ({})".format(
      car["car_make"], car["car_model"], car["car_year"])


def process_data(data):
  """Analyzes the data, looking for maximums.

  Returns a list of lines that summarize the information.
  """
  max_revenue = {"revenue": 0}
  max_sales_model = {"total_sales": 0}
  sales_by_year = {}

  for item in data:
    # Calculate the revenue generated by this model (price * total_sales)
    # We need to convert the price from "$1234.56" to 1234.56
    item_price = locale.atof(item["price"].strip("$"))
    item_revenue = item["total_sales"] * item_price
    if item_revenue > max_revenue["revenue"]:
      item["revenue"] = item_revenue
      max_revenue = item

    # TODO: also handle max sales
    car_model = item['car']['car_model']
    car_sales = item['total_sales']
    if item['total_sales'] > max_sales_model['total_sales']:
      max_sales_model = item

    # TODO: also handle most popular car_year
    car_year = item['car']['car_year']
    car_sales = item['total_sales']
    if car_year not in sales_by_year:
        sales_by_year[car_year] = car_sales
    else:
        sales_by_year[car_year] += car_sales

  print(max_sales_model)
  
  max_year = max(sales_by_year, key=sales_by_year.get)
  max_sales_by_year = sales_by_year[max_year]

  summary = [
    "The {} generated the most revenue: ${}".format(
      format_car(max_revenue["car"]), max_revenue["revenue"]),
    "The {} had the most sales: {}".format(max_sales_model['car']['car_model'], max_sales_model['total_sales']),
    "The most popular year was {} with {} sales".format(max_year, max_sales_by_year)
  ]

  return summary


def cars_dict_to_table(car_data):
  """Turns the data in car_data into a list of lists."""
  table_data = [["ID", "Car", "Price", "Total Sales"]]
  for item in car_data:
    table_data.append([item["id"], format_car(item["car"]), item["price"], item["total_sales"]])
  return table_data


def main(argv):
  """Process the JSON data and generate a full report out of it."""
  data = load_data("../car_sales.json")
  summary = process_data(data)
  new_summary = '\n'.join(summary)
  table_data = cars_dict_to_table(data)
  
  #print(summary)

  # TODO: turn this into a PDF report
  reports.generate("/tmp/cars.pdf", "Sales summary for last month", new_summary.replace('\n', '<br/>'), table_data)

  # TODO: send the PDF report as an email attachment
  sender = "automation@example.com"
  receiver = "{}@example.com".format(os.environ.get('USER'))
  subject = "Sales summary for last month"
  body = new_summary
  message = emails.generate(sender, receiver, subject, body, "/tmp/cars.pdf")
  emails.send(message)

if __name__ == "__main__":
  main(sys.argv)
