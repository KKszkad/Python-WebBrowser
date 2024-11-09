import socket
import ssl

class URL:
    def __init__(self, url):
        if "://" in url:
            self.scheme, url = url.split("://", 1)
            if self.scheme == "file":
                self.file_path = url
                return
            if self.scheme == "data":
                self.mime, self.content = url.split(",", 1)
                return
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443

            if '/' not in url:
                url = url + "/"
            self.host, url = url.split("/", 1)
            self.path = "/" + url
        else:
            parts = url.split(',')
            assert parts[0].startwith("data:"), "data URL must start with data:"

    def request(self, version = 1.0, **additional_headers):
        if self.scheme == "file":
            with open(self.file_path, 'r', encoding='utf8') as file:
                content = file.read()
                return content
        if self.scheme == "data":
            return self.content
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        request = "GET {} HTTP/{}\r\n".format(self.path, version)
        request += "Host: {}\r\n".format(self.host)
        if version == "1.1":
            # added for HTTP/1.1
            request += "Connection: close\r\n"
            request += "User-Agent: My Browser\r\n"
            for header, value in additional_headers.items():
                request += "{}: {}\r\n".format(header, value)
            # added for HTTP/1.1
        request += "\r\n"
        s.send(request.encode("utf8"))
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.lower()] = value.strip()
        s.close()
        # ! Avoid these two kinds of content return message
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()
        return content


def show(body):
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
    print()

def load(url):
    body = url.request(1.1, Accept = "text/html")
    show(body)

if __name__ == "__main__":
    import sys
    load(URL(sys.argv[1]))
    

