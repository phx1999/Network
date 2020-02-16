import asyncio
from pathlib import Path
from urllib.parse import unquote

extensions = {
    ".jpg": b'image/jpeg',
    ".txt": b'text/plain',
    ".xml": b'text/xml',
    ".png": b'image/png',
    ".json": b'application/json',
    ".pdf": b'application/pdf',
    ".docx": b'application/msword'
}

mna405 = [
    b'HTTP/1.0 405 Method Not Allowed\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n',
    b'<html><body><h1>405 Method Not Allowed</h1><body></html>\r\n',
    b'\r\n'
]

nf404 = [
    b'HTTP/1.0 404 Not Found\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n',
    b'<html><body><h1>404 Not Found</h1><body></html>\r\n',
    b'\r\n'
]


def generate_index(path: Path) -> list:
    ret = []
    dirs = [x for x in path.iterdir() if x.is_dir()]
    dirs.sort()
    for d in dirs:
        ret.append(b'<a href="' + d.name.encode() + b'/">' + d.name.encode() + b'/</a></br>')
    files = [x for x in path.iterdir() if x.is_file()]
    files.sort()
    for f in files:
        ret.append(b'<a href="' + f.name.encode() + b'">' + f.name.encode() + b'</a></br>')
    return ret


async def dispatch(reader, writer):
    data = await reader.readline()  # wait for request
    print(data)
    fields = data.decode().split(' ')
    print(fields)
    if fields[0] not in ['GET', 'HEAD']:
        writer.writelines(mna405)
        await writer.drain()
        writer.close()
        return
    dest = Path("."+unquote(fields[1]))
    print(dest)
    if not dest.exists():
        writer.writelines(nf404)
        await writer.drain()
        writer.close()
        return
    if dest.is_file():
        ctype = b'application/octet-stream'
        if dest.suffix in extensions:
            ctype = extensions[dest.suffix]
        header=[
            b'HTTP/1.0 200 OK\r\n',
            b'Content-Type: ' + ctype + b'\r\n',
            b'Content-Length: '+str(dest.stat().st_size).encode()+b'\r\n',
            b'Connection: close\r\n',
            b'\r\n'
        ]
        print(header)
        writer.writelines(header)
        file = open(str(dest),'rb')
        writer.write(file.read())
        writer.write(b'\r\n')
    else:
        writer.writelines([
            b'HTTP/1.0 200 OK\r\n',
            b'Content-Type:text/html; charset=utf-8\r\n',
            b'Connection: close\r\n',
            b'\r\n',
            b'<html><body>\r\n',
            b'<h1>Index of '+bytes(dest)+b'</h1><hr><pre>\r\n'
        ])
        writer.writelines(generate_index(dest))
        writer.writelines([
            b'</pre><hr><body></html>\r\n',
            b'\r\n'
        ])  # write response
    await writer.drain()  # break operation
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 2233, )
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
