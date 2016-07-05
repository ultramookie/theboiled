#!/usr/bin/env python

import json
import markdown
import optparse
import glob
import os
import sys
import re
import jinja2
import shutil
import feedgenerator

# Get me my config values!
def read_config(input_dir):
  config_location = input_dir + '/config.json'
  if os.path.isfile(config_location):
    with open(config_location) as config_file:    
      config = json.load(config_file)
    return config
  else:
    print 'config file %s is missing' % config_location
    sys.exit()

# What am I trying to translate?
def read_body(entry_file):
  mdfile = open(entry_file).read()
  html = markdown.markdown(mdfile)
  return html

# Where is the stuff?
def get_input_dir():
  parser = optparse.OptionParser()
  parser.add_option('-i', action="store", help="Where are your input files located?", dest="input_dir", default="./")
  (options, args) = parser.parse_args()
  return options.input_dir

# Read metadata json file and return info
def get_meta_data(entry_json):
  if os.path.isfile(entry_json):
    with open(entry_json) as json_file:
      entry_metadata = json.load(json_file)
    return entry_metadata
  else:
    print '%s.md has no associated metadata file' % base_filename

# Given the jinja for header or footer, render it to html
def render_jinja(incoming_template,metadata,config):
  title = metadata['display_title']
  year = metadata['year']
  site_name = config['site_name']
  meta_keywords = config['meta_keywords']
  meta_description = config['meta_description']
  language = config['language']
  author = config['author']
  base_url = config['base_url']
  url_location = config['url_location']
  template = jinja2.Template(incoming_template)
  rendered_jinja = template.render(
    title=title,
    year=year,
    site_name=site_name,
    meta_keywords=meta_keywords,
    meta_description=meta_description,
    language=language,
    base_url=base_url,
    url_location=url_location,
    author=author
  )
  return rendered_jinja

# Copy the style sheet into place
def copy_style(config):
  css_file = config['css_file'] 
  path,filename = os.path.split(css_file)
  dest_file = config['output'] + '/' + filename
  shutil.copyfile(css_file,dest_file)

# Create dir
def make_dir(dir):
  try:
    os.stat(dir)
  except:
    os.mkdir(dir)
    
# Get completed entry files
def get_completed_entries(input_dir):
  return sorted(glob.glob(input_dir + '/*/*.md'), reverse=False)
    
# Do the doing
def process_entries(input_dir,config):
  header_template = open(config['header_file']).read()
  footer_template = open(config['footer_file']).read()
  entry_files = glob.glob(input_dir + '/*.md')
  for entry_file in entry_files:
    base_filename = os.path.splitext(entry_file)[0]
    entry_json = base_filename + '.json'
    metadata = get_meta_data(entry_json)
    sort_title = metadata['sort_title']
    first_letter = sort_title[0].lower()
    processed_dir = '%s/%s' % (input_dir,first_letter)
    path,filename = os.path.split(base_filename)
    header_html = render_jinja(header_template,metadata,config)
    footer_html = render_jinja(footer_template,metadata,config)
    body_html = read_body(entry_file)
    html_doc = header_html + body_html + footer_html
    output_dir = '%s/%s' % (config['output'],first_letter)
    make_dir(processed_dir)
    make_dir(output_dir)
    html_filename = '%s/%s.html' % (output_dir,filename)
    blog_file = open(html_filename,'w')
    blog_file.write(html_doc)
    blog_file.close()
    if os.path.isfile(html_filename):
      shutil.move(entry_file,processed_dir)
      shutil.move(entry_json,processed_dir)
      print '%s has been processed.' % entry_file

# Let people find their way around
def create_index_page(input_dir,config):
  index_filename = config['output'] + '/index.html'
  prev_letter = ''
  author = config['author']
  metadata = { "display_title": config['site_name'], "sort_title": config['site_name'], "year": "" }
  output_dir = config['output']
  header_template = open(config['header_file']).read()
  footer_template = open(config['footer_file']).read()
  header_html = render_jinja(header_template,metadata,config)
  footer_html = render_jinja(footer_template,metadata,config)
  entry_files = get_completed_entries(input_dir)
  index_filecontents = header_html 
  for entry_file in entry_files:
    base_filename = os.path.splitext(entry_file)[0]
    entry_json = base_filename + '.json'
    metadata = get_meta_data(entry_json)
    path,filename = os.path.split(base_filename)
    title = metadata['display_title']
    sort_title = metadata['sort_title']
    year = metadata['year']
    cur_letter = sort_title[0].lower()
    html_filename = '%s/%s.html' % (cur_letter,filename)
    if cur_letter != prev_letter:
      index_filecontents = '%s <h1>%s</h1>' % (index_filecontents,cur_letter)
      prev_letter = cur_letter
    index_filecontents = '%s <a href="%s">%s</a> (%s) <br />' % (index_filecontents,html_filename,title,year)
  index_filecontents = index_filecontents + footer_html
  index_file = open(index_filename,'w')
  index_file.write(index_filecontents)
  index_file.close()


# Go Speed Go
def run():
  input_dir = get_input_dir()
  config = read_config(input_dir)
  copy_style(config)
  process_entries(input_dir,config)
  create_index_page(input_dir,config)

# Make it so!
run()
