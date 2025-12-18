def parse_body(body):
    if body is None:
        return []

    def get_data():
        for sec in body.iterfind('sec'):
            title = sec.find('title').text
            sec = sec.find('sec') if sec.find('sec') is not None else sec
            text = '\n\n'.join(''.join(p.itertext()) for p in sec.findall('p'))
            yield {'title': title, 'text': text}
    body = list(get_data())
    return body