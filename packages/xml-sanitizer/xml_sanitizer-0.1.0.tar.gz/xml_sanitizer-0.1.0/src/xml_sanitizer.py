import re 

def xml_content_cleanup(xml_text):
    # Replace & not followed by an entity with &amp;
    xml_text = re.sub(r'&(?!amp;|lt;|gt;|apos;|quot;)', '&amp;', xml_text)
    return xml_text

