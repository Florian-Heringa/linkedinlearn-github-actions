import yaml
import xml.etree.ElementTree as ElementTree
from collections import namedtuple

# Load yaml source data
with open('feed.yaml', 'r') as yf:
    yaml_data = yaml.safe_load(yf) 

# Build base xml element for rss feed
rss_element = ElementTree.Element('rss', {
        'version': '2.0',
        'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/'
    })

# Add channel root
channel_element = ElementTree.SubElement(rss_element, 'channel')

# Define channel fields
Element = namedtuple('Element', ('name', 'has_prefix', 'override'))
elements: list[Element] = [
    Element('title', False, None),
    Element('format', False, None),
    Element('subtitle', False, None),
    Element('author', True, None),
    Element('description', False, None),
    Element('language', False, None),
    Element('link', False, None),
] 

# Add channel fields
for element in elements:
    ElementTree.SubElement(channel_element, f"{'itunes:' if element.has_prefix else ''}{element.name}").text = yaml_data[element.name]

# Add fields with a separate structure
link_prefix = yaml_data['link']
ElementTree.SubElement(channel_element, 'itunes:image', {'href': f'{link_prefix}{yaml_data['image']}'})
ElementTree.SubElement(channel_element, 'itunes:category', {'text': yaml_data['category']})

# Each item (episode) has its own fields
item_elements: list[Element] = [
    Element('title', False, None),
    Element('author', True, yaml_data['author']),
    Element('description', False, None),
    Element('duration', True, None),
    Element('pubDate', False, None),
]

# Add items
for item in yaml_data['item']:
    item_element = ElementTree.SubElement(channel_element, 'item')
    for element in item_elements:
        ElementTree.SubElement(
            item_element, 
            f"{'itunes:' if element.has_prefix else ''}{element.name}"
            ).text = item[element.name] if element.override is None else element.override
        
    enclosure = ElementTree.SubElement(item_element, 'enclosure', {
        'url': link_prefix + item['file'],
        'type': 'audio/mp3',
        'length': item['length']
    })

# Save as .xml file
output_tree = ElementTree.ElementTree(rss_element)
output_tree.write('podcast.xml', encoding='UTF-8', xml_declaration=True)