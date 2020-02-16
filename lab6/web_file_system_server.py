import asyncio
from pathlib import Path
from urllib.parse import unquote

mime_types = {'html': 'text/html', 'htm': 'text/html', 'shtml': 'text/html', 'css': 'text/css', 'xml': 'text/xml',
              'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpeg', 'js': 'application/javascript',
              'atom': 'application/atom+xml', 'rss': 'application/rss+xml', 'mml': 'text/mathml', 'txt': 'text/plain',
              'jad': 'text/vnd.sun.j2me.app-descriptor', 'wml': 'text/vnd.wap.wml', 'htc': 'text/x-component',
              'png': 'image/png', 'svg': 'image/svg+xml', 'svgz': 'image/svg+xml', 'tif': 'image/tiff',
              'tiff': 'image/tiff', 'wbmp': 'image/vnd.wap.wbmp', 'webp': 'image/webp', 'ico': 'image/x-icon',
              'jng': 'image/x-jng', 'bmp': 'image/x-ms-bmp', 'woff': 'font/woff', 'woff2': 'font/woff2',
              'jar': 'application/java-archive', 'war': 'application/java-archive', 'ear': 'application/java-archive',
              'json': 'application/json', 'hqx': 'application/mac-binhex40', 'doc': 'application/msword',
              'pdf': 'application/pdf', 'ps': 'application/postscript', 'eps': 'application/postscript',
              'ai': 'application/postscript', 'rtf': 'application/rtf', 'm3u8': 'application/vnd.apple.mpegurl',
              'kml': 'application/vnd.google-earth.kml+xml', 'kmz': 'application/vnd.google-earth.kmz',
              'xls': 'application/vnd.ms-excel', 'eot': 'application/vnd.ms-fontobject',
              'ppt': 'application/vnd.ms-powerpoint', 'odg': 'application/vnd.oasis.opendocument.graphics',
              'odp': 'application/vnd.oasis.opendocument.presentation',
              'ods': 'application/vnd.oasis.opendocument.spreadsheet', 'odt': 'application/vnd.oasis.opendocument.text',
              'wmlc': 'application/vnd.wap.wmlc', '7z': 'application/x-7z-compressed', 'cco': 'application/x-cocoa',
              'jardiff': 'application/x-java-archive-diff', 'jnlp': 'application/x-java-jnlp-file',
              'run': 'application/x-makeself', 'pl': 'application/x-perl', 'pm': 'application/x-perl',
              'prc': 'application/x-pilot', 'pdb': 'application/x-pilot', 'rar': 'application/x-rar-compressed',
              'rpm': 'application/x-redhat-package-manager', 'sea': 'application/x-sea',
              'swf': 'application/x-shockwave-flash', 'sit': 'application/x-stuffit', 'tcl': 'application/x-tcl',
              'tk': 'application/x-tcl', 'der': 'application/x-x509-ca-cert', 'pem': 'application/x-x509-ca-cert',
              'crt': 'application/x-x509-ca-cert', 'xpi': 'application/x-xpinstall', 'xhtml': 'application/xhtml+xml',
              'xspf': 'application/xspf+xml', 'zip': 'application/zip', 'bin': 'application/octet-stream',
              'exe': 'application/octet-stream', 'dll': 'application/octet-stream', 'deb': 'application/octet-stream',
              'dmg': 'application/octet-stream', 'iso': 'application/octet-stream', 'img': 'application/octet-stream',
              'msi': 'application/octet-stream', 'msp': 'application/octet-stream', 'msm': 'application/octet-stream',
              'mid': 'audio/midi', 'midi': 'audio/midi', 'kar': 'audio/midi', 'mp3': 'audio/mpeg', 'ogg': 'audio/ogg',
              'm4a': 'audio/x-m4a', 'ra': 'audio/x-realaudio', '3gpp': 'video/3gpp', '3gp': 'video/3gpp',
              'ts': 'video/mp2t', 'mp4': 'video/mp4', 'mpeg': 'video/mpeg', 'mpg': 'video/mpeg',
              'mov': 'video/quicktime', 'webm': 'video/webm', 'flv': 'video/x-flv', 'm4v': 'video/x-m4v',
              'mng': 'video/x-mng', 'asx': 'video/x-ms-asf', 'asf': 'video/x-ms-asf', 'wmv': 'video/x-ms-wmv',
              'avi': 'video/x-msvideo'}
# post 方法
InvalidMethod = [
    b'HTTP/1.0 405 Method Not Allowed\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n',
    b'<html><body><h1>405 Method Not Allowed</h1><body></html>\r\n',
    b'\r\n'
]
# 找不到文件
NotFound = [
    b'HTTP/1.0 404 Not Found\r\n',
    b'Content-Type:text/html; charset=utf-8\r\n',
    b'Connection: close\r\n',
    b'\r\n',
    b'<html><body><h1>404 Not Found</h1><body></html>\r\n',
    b'\r\n'
]


async def dispatch(reader, writer):
    message = []
    while True:
        data = await reader.readline()
        message.append(data.decode())
        if data == b'\r\n' or data == b'':
            break
    head = message[0].split(" ")
    range_start = 0
    range_end = -1
    r = False
    iscookie = False
    path = Path("." + unquote(head[1]))  # get path
    print(path)
    size = path.stat().st_size
    isreferer = True
    for line in message:
        line = line.split(" ")
        print(line)
        if line[0] == 'Range:':
            r1 = line[1].split("=")
            if r1[0] == 'byte':
                range_int = r1[1].split("-")
                if range_int[0] != '':
                    range_start = int(range_int[0])
                if range_int[1] != '\r\n':
                    range_end = int(range_int[1])
                    if range_int[0] == '':
                        range_start = range_end+size
            r = True
        elif line[0] == 'Cookie:' and line[1].split("=")[1] != '.\r\n':
            iscookie = True
            link = line[1].split("=")[1]
        elif line[0] == 'Referer:':
            isreferer = False
    print("isreferer " + str(isreferer))
    print(path)
    print("iscookie " + str(iscookie))
    if head[0] not in ['GET', 'HEAD']:  # 判断head
        writer.writelines(InvalidMethod)
        await writer.drain()
        writer.close()
        return
    if not path.exists():
        writer.writelines(NotFound)
        await writer.drain()
        writer.close()
        return
    elif path.is_file():
        print("is file")
        f_type = b'Application/octet-stream'
        if path.suffix in mime_types:
            f_type = mime_types[path.suffix]  # 判断文件类型
        print(f_type)
        if head[0] == 'GET':
            if r:
                if range_end < 0:
                    range_end += size
                writer.writelines([
                    b'HTTP/1.1 206 Partial Content\r\n',
                    b'Content-Type: ' + f_type + b'\r\n',
                    b'Content-Range: bytes' + str(range_start).encode() + b'-' + str(
                        range_end).encode() + b'/' + str(size).encode() + b'\r\n',
                    b'Content-Length: ' + str(range_end - range_start).encode() + b'\r\n',
                    b'Connection: close\r\n',
                    b'\r\n'
                ])
                print("open")
                file = open(str(path), 'rb')
                file.seek(range_start, 0)
                content = file.read(range_end - range_start + 1)
                file.close()
                writer.write(content)  # 打开文件
                writer.write(b'\r\n')
            else:
                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type: ' + f_type + b'\r\n',
                    b'Content-Length: ' + str(path.stat().st_size).encode() + b'\r\n',
                    b'Connection: close\r\n',
                    b'\r\n'
                ])
                print("open")
                file = open(str(path), 'rb')
                writer.write(file.read())  # 打开文件
                writer.write(b'\r\n')
        else:
            if r:
                size = path.stat().st_size
                if range_end < 0:
                    range_end += size
                writer.writelines([
                    b'HTTP/1.1 206 Partial Content\r\n',
                    b'Content-Type: ' + f_type + b'\r\n',
                    b'Content-Range: bytes' + str(range_start).encode() + b'-' + str(
                        range_end).encode() + b'/' + str(size).encode() + b'\r\n',
                    b'Content-Length: ' + str(range_end - range_start).encode() + b'\r\n',
                    b'Connection: close\r\n',
                    b'\r\n'
                ])
            else:
                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type: ' + f_type + b'\r\n',
                    b'Content-Length: ' + str(path.stat().st_size).encode() + b'\r\n',
                    b'Connection: close\r\n',
                    b'\r\n'
                ])
    else:
        print("is dir")
        if head[0] == 'GET':
            if head[1] == '/' and iscookie and isreferer:
                path = Path("./" + unquote(link).strip("\r\n"))
                print(path)
                print("in cookie")
                writer.writelines([
                    b'HTTP/1.0 302 Moved Temporarily\r\n',
                    b'Content-Type: text/html; charset=utf-8\r\n',
                    b'Connection: close\r\n',
                    b'Location: ' + str(path).encode() + b'/\r\n',
                    b'Set-Cookie: customer=' +
                    str(path).encode() + b';expires= Wednesday, 19-OCT-23 23:12:40 GMT; Path=/\r\n',
                    b'\r\n',
                    b'<html><body>\r\n',
                    b'<h1>Index of ' + str(path).encode() + b'</h1><hr><pre>\r\n'
                ])
                for x in path.iterdir():
                    if not x.is_file():
                        writer.writelines([
                            b'<a href="' + x.name.encode() + b'/">' + x.name.encode() + b'/</a></br>'])  # 文件夹超链接
                for x in path.iterdir():
                    if x.is_file():
                        writer.writelines([
                            b'<a href="' + x.name.encode() + b'"><b><big>' + x.name.encode() + b'</big></b></a></br>'])  # 文件超链接
                writer.writelines([
                    b'</pre><hr><body></html>\r\n',
                    b'\r\n'
                ])
            else:
                writer.writelines([
                    b'HTTP/1.0 200 OK\r\n',
                    b'Content-Type:text/html; charset=utf-8\r\n',
                    b'Connection: close\r\n',
                    b'Set-Cookie: customer=' +
                    str(path).encode() + b';expires= Wednesday, 19-OCT-23 23:12:40 GMT; Path=/\r\n',
                    b'\r\n',
                    b'<html><body>\r\n',
                    b'<h1>Index of ' + str(path).encode() + b'</h1><hr><pre>\r\n'
                ])
                writer.writelines([
                    b'<a href="../">../</a></br>'])
                for x in path.iterdir():
                    if not x.is_file():
                        writer.writelines([
                            b'<a href="' + x.name.encode() + b'/">' + x.name.encode() + b'/</a></br>'])  # 文件夹超链接
                for x in path.iterdir():
                    if x.is_file():
                        writer.writelines([
                            b'<a href="' + x.name.encode() + b'"><b><big>' + x.name.encode() + b'</big></b></a></br>'])  # 文件超链接
                writer.writelines([
                    b'</pre><hr><body></html>\r\n',
                    b'\r\n'
                ])
        else:
            writer.writelines([
                b'HTTP/1.0 200 OK\r\n',
                b'Content-Type:text/html; charset=utf-8\r\n',
                b'Connection: close\r\n',
                b'Set-Cookie: customer=' +
                str(path).encode() + b';expires= Wednesday, 19-OCT-23 23:12:40 GMT; Path=/\r\n',
                b'\r\n',
                b'<html><body>\r\n',
                bytes('<html><head><title>Index of ' + str(path) + '</title></head>', 'utf-8'),
                b'</pre><hr><body></html>\r\n',
                b'\r\n'
            ])
    await writer.drain()
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, )
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
