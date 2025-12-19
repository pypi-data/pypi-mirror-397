'''
This module handles the extraction of parts from 
multipart/form-data-encoded HTTP content.

'''

crlf = bytearray([13,10])
hyphens = bytearray([45,45])
crlfhyphens = bytearray([13,10,45,45])

def get_parts(response_content, boundary):
    '''
    Get the parts of a multipart response.
    
    Parameters:
      * response_content(bytes): the content of the response.
      * boundary(str) the boundary between the parts, not including
      the prefixed '--' or the following '--' or carriage-return and
      line feed.
      
    Raises:
      * PartException
    
    Returns:
      * the parts in the content of the response.
    '''
    
    parts = {}
    prefixed_boundary = bytearray(hyphens)
    prefixed_boundary.extend(boundary.encode())
    crlfprefixed_boundary = bytearray(crlfhyphens)
    crlfprefixed_boundary.extend(boundary.encode())
    part_start = response_content.find(prefixed_boundary)
    if part_start < 0: raise PartException('No parts')
    if not response_content.startswith(crlf, part_start + len(prefixed_boundary)): 
        raise PartException('Invalid first boundary')
    part_start = part_start + len(prefixed_boundary) + 2
    while True:
        part_end = response_content.find(crlfprefixed_boundary, part_start)
        if part_end < 0: raise PartException('Part end not found')
        part = Part(response_content, part_start, part_end)
        __set_part_headers(part)
        parts[part.name] = part
        if response_content.startswith(hyphens, part_end + len(crlfprefixed_boundary)): break
        if not response_content.startswith(crlf, part_end + len(crlfprefixed_boundary)): 
            raise PartException('Invalid part end boundary')
        part_start = part_end + len(prefixed_boundary) + 4
    return parts


class Part:
    '''
    A part of a multipart response.
    '''
    
    def __init__(self, response_content, start, end):
        '''
        Construct a part of a multipart response.
        
        Parameters:
          * response_content(bytes): the content of the response.
          * start(int): the start of the part in the content of 
            the response.
          * end(int): the end of the part in the content of 
            the response. (The last byte of the part
            is at end - 1 )
        '''
        
        self.response_content = response_content
        self.header_segments = []
        self.headers = {}
        header_start = start
        while True:
            header_end = response_content.find(crlf, header_start)
            if header_end < header_start: raise PartException('Invalid part')
            if header_end == header_start: break
            self.header_segments.append((header_start, header_end))
            header_start = header_end + 2
        self.content_start = header_start + 2
        self.content_end = end
        
        
    def content(self):
        return self.response_content[self.content_start: self.content_end]


def __set_part_headers(part):
    '''
    Set the headers of a part.
    
    When a part is constructed, the starts and ends of the headers are
    identified, but the headers are not constructed. (Python does not 
    easily allow the instantiation of one class while instantiating
    another). This method instantiates the headers.
    
    Parameters:
      * the part whose headers are to be instantiated.
      
    Raises:
      * PartException
    '''
    
    for header_segment in part.header_segments:
        header_text = part.response_content[header_segment[0]:header_segment[1]].decode()
        header = Header(header_text)
        part.headers[header.name] = header
    content_disposition_header = part.headers['content-disposition']
    if content_disposition_header is None: raise PartException('Missing part content disposition')
    part.name = content_disposition_header.parms['name']
    if part.name is None: raise PartException('Missing part name')
    

class Header:
    '''
    A header of the response or a part of the response.
    '''
    
    def __init__(self, line):
        '''
        Construct a header.
        
        Parameters:
          * line(str): a text line containing a header, without the terminating
          carriage return and line feed.
          
        Raises:
          * 'PartException'
        '''
        
        segments = line.split(';')
        name_segment = segments[0].strip()
        colonix = name_segment.find(':')
        if colonix < 0: raise PartException('Invalid header: ' + line)
        self.name = name_segment[:colonix].lower()
        self.value = name_segment[colonix+1:].lower()
        self.parms = {}
        for i in range(1,len(segments)):
            segment = segments[i]
            eqix = segment.find('=')
            if eqix > 0:
                parmname = segment[:eqix].strip()
                parmval = segment[eqix+1:].strip()
                if parmval[0] == '"' and parmval[len(parmval)-1] == '"':
                    parmval = parmval[1:len(parmval)-1]
                self.parms[parmname] = parmval

                  
    def get_parm(self, name):
        return self.parms[name]


class PartException(RuntimeError):
    '''
    A run-time exception occurring during extraction of the parts
    of a multipart response.
    '''
    def __init__(self, *messages):
        super().__init__(*messages)
