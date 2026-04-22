import re

# 原始混淆字符串（从 eval 的第一个参数）
packed_string = r'b\x20L(e,t,a,o,d){5(o||(o=!1),d||(d=!1),\x227\x22===e.2.3){4\x20r=$(e).B(\x22v\x22);5(r.M>0&&r[0].8>0)w\x20x\x20j.C(\x22圖片已正確處理，跳過:\x22,e.6);j.C(\x22檢測到 v 丟失，重新處理:\x22,e.6),e.2.3=\x22N\x22}5(e.O.P(\x22.Q\x22)>0||y(t)<y(a)||\x221\x22==d)w\x22R\x22===e.9.k&&(e.9.k=\x22z\x22),x(e.2.3=\x227\x22);1==o||0==e.S?e.T=b(){q(e)}:q(e)}b\x20q(e){5(\x227\x22!==e.2.3){4\x20t,a=e.U,o;5(a&&\x22V\x22===a.W)(o=(t=a).D(\x22E\x22)).X(0,0,t.8,t.F);Y(t=Z.10(\x22v\x22)).9.k=\x22z\x22,e.11(t);4\x20o=t.D(\x22E\x22),d=e.8,r=e.12,s=e.13;5(0===r||0===s)w\x20j.14(\x22圖片尺寸異常，延遲處理:\x22,e.6),x\x2015(b(){e.2.3||q(e)},16);t.8=r,t.F=s,(d>e.A.G||0==d)&&(d=e.A.G),t.9.8=d+\x2217\x22;4\x20n=e.A.6||e.6;n=n.H(\x22.\x22)[0];4\x20i,l=$(e).18(\x2219-1a-I\x22)||I;n.1b(\x22B\x22)&&(n=n.H(\x221c\x22).1d());1e{1f(4\x20c=1g(J.K(l),J.K(n)),f=y(s%c),m=r,g=0;g<c;g++){4\x20h=1h.1i(s/c),u=h*g,p=s-h*(g+1)-f;0==g?h+=f:u+=f,o.1j(e,0,p,m,h,0,u,m,h)}e.2.3=\x227\x22,$(e).1k(\x221l\x22)}1m(t){j.1n(\x22圖片重組失敗:\x22,t,e.6),e.9.k=\x22z\x22,e.2.3=\x227\x22}}}'

# 解码 \xNN 转义
def unescape_string(s):
    result = []
    i = 0
    while i < len(s):
        if s[i:i+2] == '\\x' and i+4 <= len(s):
            hex_val = int(s[i+2:i+4], 16)
            result.append(chr(hex_val))
            i += 4
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

packed_code = unescape_string(packed_string)

# 关键字数组（从 _0x4c12() 返回的数组索引 12 开始）
keywords_str = '||dataset|scrambleProcessed|var|if|id|true|width|style||function||||||||console|display||||||onImageLoadedForNew|||||canvas|return|void|parseInt|block|parentNode|next|log|getContext|2d|height|offsetWidth|split|aid|window|btoa|scramble_image_for_new|length|false|src|indexOf|gif|none|complete|onload|nextElementSibling|CANVAS|tagName|clearRect|else|document|createElement|after|naturalWidth|naturalHeight|warn|setTimeout|100|px|attr|data|chapter|includes|_|pop|try|for|get_num|Math|floor|drawImage|addClass|hide|catch|error'
keywords = keywords_str.split('|')

# 创建非空关键字到索引的映射
keyword_map = {}
for i, kw in enumerate(keywords):
    if kw:
        keyword_map[i] = kw

# 基数 62 字符集
BASE62_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def base62_decode(s):
    """将 base62 编码字符串转换为数字"""
    result = 0
    for c in s:
        result = result * 62 + BASE62_CHARS.index(c)
    return result

# 构建完整的替换映射
# 首先找出所有数字形式的引用并替换为关键字
def replace_keywords(code):
    # 按长度降序排序，先替换长的数字（如 19, 11），再替换短的（如 9, 8）
    sorted_indices = sorted(keyword_map.keys(), reverse=True)
    
    for idx in sorted_indices:
        kw = keyword_map[idx]
        # 将数字转换为 base62 编码形式
        encoded = ''
        num = idx
        if num == 0:
            encoded = '0'
        else:
            while num > 0:
                encoded = BASE62_CHARS[num % 62] + encoded
                num //= 62
        
        # 替换：需要确保是独立的标识符（前后不是字母数字）
        # 使用正则表达式进行单词边界匹配
        pattern = r'(?<![0-9a-zA-Z_])' + re.escape(encoded) + r'(?![0-9a-zA-Z_])'
        code = re.sub(pattern, kw, code)
    
    return code

# 应用关键字替换
decoded = replace_keywords(packed_code)

print("=== 关键字替换后的代码 ===")
print(decoded)
print("\n")

# 现在处理其他压缩/混淆的符号
# 根据上下文推断额外映射
extra_replacements = {
    # 单字母变量映射（基于上下文）
    '.k': '.display',  # style.display 中的 display 被压缩为 k
    '.F': '.height',   # height 被压缩为 F
    '.W': '.tagName',  # tagName 被压缩为 W
    '.M': '.length',   # length 被压缩为 M
    
    # 函数名映射
    '.B(': '.attr(',
    '.C(': '.log(',
    '.14(': '.warn(',
    '.1n(': '.error(',
    '.D(': '.getContext(',
    '.X(': '.fillRect(',
    '.10(': '.createElement(',
    '.11(': '.after(',
    '.H(': '.split(',
    '.18(': '.attr(',
    '.1b(': '.attr(',
    '.1k(': '.addClass(',
    '.1j(': '.drawImage(',
    '.K(': '(',  # get_num 可能是直接调用
    
    # 对象引用
    'j.': 'console.',
    'Z.': 'document.',
    'J.': '',  # J 可能是 window 或全局对象
    
    # 控制流关键字（已被关键字替换覆盖，但保留作为检查）
    '=!1': '=false',
    '!1': 'false',
    
    # 字符串常量映射
    '"7"': '"block"',
    '"N"': '"none"',
    '"z"': '"none"',
    '"R"': '"CANVAS"',
    '"V"': '"CANVAS"',
    '"E"': '"2d"',
    '"v"': '"canvas"',
    '".Q"': '".gif"',
    '"17"': '"px"',
    '"1l"': '"scrambleProcessed"',
    '"19-1a-I"': '"data-chapter-id"',
    '"B"': '"aid"',
    '"1c"': '"next"',
    '"1"': '"1"',  # 保持不变
    
    # 其他
    'y(': 'parseInt(',
    '1h.': 'Math.',
    '.1i(': '.floor(',
    '15(': 'setTimeout(',
    '1g(': '',  # 可能是空或特定函数
}

# 应用额外替换（按长度降序）
for old, new in sorted(extra_replacements.items(), key=lambda x: -len(x[0])):
    decoded = decoded.replace(old, new)

print("=== 进一步解码后的代码 ===")
print(decoded)
