import socket
import ssl

def parsed_url(url):
    """
    解析 url 返回 (protocol host port path)
    """
    # 检查协议
    protocol = 'http'
    if url[:7] == 'http://':
        u = url.split('://')[1]
    elif url[:8] == 'https://':
        protocol = 'https'
        u = url.split('://')[1]
    else:
        # '://' 定位 然后取第一个 / 的位置来切片
        u = url

    # 检查默认 path
    i = u.find('/')
    if i == -1:
        host = u
        path = '/'
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        'http': 80,
        'https': 443,
    }
    # 默认端口
    port = port_dict[protocol]
    if host.find(':') != -1:
        h = host.split(':')
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


def socket_by_protocol(protocol):
    """
    根据协议返回一个 socket 实例
    """
    if protocol == 'http':
        s = socket.socket()
    else:
        # HTTPS 协议需要使用 ssl.wrap_socket 包装一下原始的 socket
        # 除此之外无其他差别
        s = ssl.wrap_socket(socket.socket())
    return s


def response_by_socket(s):
    """
    参数是一个 socket 实例
    返回这个 socket 读取的所有数据
    """
    response = b''
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response


def parsed_response(r):
    """
    把 response 解析出 状态码 headers body 返回
    状态码是 int
    headers 是 dict
    body 是 str
    """
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body


# 复杂的逻辑全部封装成函数
def get(url):
    """
    用 GET 请求 url 并返回响应
    """
    protocol, host, port, path = parsed_url(url)

    s = socket_by_protocol(protocol)
    s.connect((host, port))

    request = 'GET {} HTTP/1.1\r\nhost: {}\r\nConnection: close\r\nCookie: user=ssk2fdfdka9e8aa9\r\n\r\n'.format(path, host)
    encoding = 'utf-8'
    s.send(request.encode(encoding))

    response = response_by_socket(s)
    r = response.decode(encoding)

    status_code, headers, body = parsed_response(r)
    if status_code == 301:
        url = headers['Location']
        return get(url)

    return status_code, headers, body


class Movie(object):
    def __init__(self):
        self.name = []
        self.point = []
        self.fans = []
        self.quotation = []

m = Movie()

left_list = [
    ('<span class="title">', m.name),
    ('<span class="rating_num" property="v:average">', m.point),
    ('<span>', m.fans),
    ('<span class="inq">', m.quotation),
]
right = '</span>'

width_dict = {
    0: 10,
    1: 5,
    2: 10,
    3: 30,
}


def ljust(s, width, fillchar='  '):
    a = width - len(s)
    if a >= 0:
        s = s + fillchar * a
    return s


def max_list(n, body_list):
    x = []
    y = []
    m = 1700
    for i, s in enumerate(body_list):
        y.append(len(str(s)))
        bbb = len(str(s)) - m
        if i == 0 or i == n - 1:
            if bbb > 10000:
                x.append(i)
        elif len(str(s)) - m > 1000:
            x.append(i)
    return x


def find_between(body, left_list, right):
    for i, left in enumerate(left_list):
        body_list = body.split(left[0])
        num = len(body_list)
        if num != 26 and left[0] == '<span class="inq">':
            code = max_list(num, body_list)
        else:
            code = []
        index = 0
        j = 1
        mark = 0
        while index < 25:
            if mark < len(code):
                if index == code[mark]:
                    x = '暂无'
                    mark += 1
                    j -= 1
                else:
                    x = body_list[j].split(right, 1)[0]
            else:
                x = body_list[j].split(right, 1)[0]
            j += 1
            if '&nbsp' in x:
                continue
            elif left[0] == '<span>':
                s = len(x)
                try:
                    int(x[:s - 3])
                except ValueError:
                    continue
            x = ljust(x, width_dict[i], fillchar='  ')
            index += 1
            left[1].append(x)


if __name__ == '__main__':
    url = 'https://movie.douban.com/top250'
    query = {}
    s = 0
    while query.get('start') != 225:
        query['start'] = 25 * s
        print('-' * 50, '第{}页'.format(query.get('start') // 25 + 1), '-' * 50)
        n = 25 * s
        body = get(url)[2]
        find_between(body, left_list, right)
        for i in range(n, n + 25):
            movie = '{}{:3} 电影名:{} 打分:{} 评价人数:{} 引用语:{}'.format('No', i + 1, m.name[i], m.point[i], m.fans[i], m.quotation[i])
            print(movie)
        s += 1
