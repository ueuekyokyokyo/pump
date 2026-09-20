def url_decode(text):
    result = bytearray()
    i = 0

    while i < len(text):
        if text[i] == '+':
            result.append(32)
            i += 1
        elif text[i] == '%' and i + 2 < len(text):
            try:
                result.append(int(text[i + 1:i + 3], 16))
                i += 3
            except:
                result.append(ord('%'))
                i += 1
        else:
            result.append(ord(text[i]))
            i += 1

    return result.decode('utf-8')


def get_query_value(request, key):
    key = key + '='
    start = request.find(key)

    if start == -1:
        return None

    start += len(key)
    end = request.find('&', start)

    if end == -1:
        end = request.find(' ', start)

    value = request[start:end]
    return url_decode(value)