import re
import json

# 这是从混淆代码中提取的关键字数组（索引12开始是关键字列表）
keywords_str = '||dataset|scrambleProcessed|var|if|id|true|width|style||function||||||||console|display||||||onImageLoadedForNew|||||canvas|return|void|parseInt|block|parentNode|next|log|getContext|2d|height|offsetWidth|split|aid|window|btoa|scramble_image_for_new|length|false|src|indexOf|gif|none|complete|onload|nextElementSibling|CANVAS|tagName|clearRect|else|document|createElement|after|naturalWidth|naturalHeight|warn|setTimeout|100|px|attr|data|chapter|includes|_|pop|try|for|get_num|Math|floor|drawImage|addClass|hide|catch|error'

keywords = keywords_str.split('|')

# 创建反向映射：非空关键字 -> 索引
keyword_to_index = {}
for i, kw in enumerate(keywords):
    if kw:
        keyword_to_index[kw] = i

# 基数62编码解码函数 (与混淆器中的 _3d4fca 相反)
def base62_encode(num):
    """将数字转换为基数62编码（小写a-z + 大写A-Z + 0-9）"""
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if num == 0:
        return chars[0]
    result = ''
    while num > 0:
        result = chars[num % 62] + result
        num //= 62
    return result

def base62_decode(s):
    """将基数62编码转换回数字"""
    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = 0
    for c in s:
        result = result * 62 + chars.index(c)
    return result

# 压缩的代码字符串（已转义）
packed_code = r'b L(e,t,a,o,d){5(o||(o=!1),d||(d=!1),"7"===e.2.3){4 r=$(e).B("v");5(r.M>0&&r[0].8>0)w x j.C("圖片已正確處理，跳過:",e.6);j.C("檢測到 v 丟失，重新處理:",e.6),e.2.3="N"}5(e.O.P(".Q")>0||y(t)<y(a)||"1"==d)w"R"===e.9.k&&(e.9.k="z"),x(e.2.3="7");1==o||0==e.S?e.T=b(){q(e)}:q(e)}b q(e){5("7"!==e.2.3){4 t,a=e.U,o;5(a&&"V"===a.W)(o=(t=a).D("E")).X(0,0,t.8,t.F);Y(t=Z.10("v")).9.k="z",e.11(t);4 o=t.D("E"),d=e.8,r=e.12,s=e.13;5(0===r||0===s)w j.14("圖片尺寸異常，延遲處理:",e.6),x 15(b(){e.2.3||q(e)},16);t.8=r,t.F=s,(d>e.A.G||0==d)&&(d=e.A.G),t.9.8=d+"17";4 n=e.A.6||e.6;n=n.H(".")[0];4 i,l=$(e).18("19-1a-I")||I;n.1b("B")&&(n=n.H("1c").1d());1e{1f(4 c=1g(J.K(l),J.K(n)),f=y(s%c),m=r,g=0;g<c;g++){4 h=1h.1i(s/c),u=h*g,p=s-h*(g+1)-f;0==g?h+=f:u+=f,o.1j(e,0,p,m,h,0,u,m,h)}e.2.3="7",$(e).1k("1l")}1m(t){j.1n("圖片重組失敗:",t,e.6),e.9.k="z",e.2.3="7"}}}'

# 首先处理 \xNN 转义
def unescape_string(s):
    result = []
    i = 0
    while i < len(s):
        if s[i:i+2] == '\\x' and i+4 < len(s):
            hex_val = int(s[i+2:i+4], 16)
            result.append(chr(hex_val))
            i += 4
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)

packed_code = unescape_string(packed_code)

print("=== 解压缩后的代码 ===")
print(packed_code)
print("\n")

# 分析代码中使用的单字符/短标识符映射
# 从代码中可以看到一些明显的映射：
# e.2.3 -> e.style.display (2->style, 3->display)
# e.2 -> style
# e.3 -> display
# e.8 -> width
# e.6 -> src
# etc.

# 让我们创建一个更智能的替换映射
replacements = {
    # 对象属性映射（基于上下文推断）
    '.2.': '.style.',
    '.2.': '.style.',
    '.3': '.display',
    '.8': '.width',  
    '.6': '.src',
    '.9.': '.style.',
    '.9.k': '.style.display',
    '.9.8': '.style.width',
    '.A.': '.dataset.',
    '.A.G': '.dataset.height',
    '.A.6': '.dataset.src',
    '.U': '.dataset.scrambleProcessed',
    '.S': '.complete',
    '.T': '.onload',
    '.12': '.naturalWidth',
    '.13': '.naturalHeight',
    '.O.P': '.src.indexOf',
    
    # 函数调用映射
    '$(e).B(': '$(e).attr(',
    'j.C(': 'console.log(',
    'j.14(': 'console.warn(',
    'j.1n(': 'console.error(',
    '.D(': '.getContext(',
    '.X(': '.fillRect(',
    '.10(': '.createElement(',
    '.11(': '.after(',
    '.H(': '.split(',
    '.18(': '.attr(',
    '.1b(': '.attr(',
    '.1k(': '.addClass(',
    '.1j(': '.drawImage(',
    '15(': 'setTimeout(',
    'y(': 'parseInt(',
    '1h.': 'Math.',
    '.1i(': '.floor(',
    'J.K(': 'get_num(',
    
    # 变量和常量
    '=!1': '=false',
    '=!0': '=true',
    '!1': 'false',
    '!0': 'true',
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
    
    # 控制流
    'b ': 'function ',
    '4 ': 'var ',
    '5(': 'if(',
    '5(': 'if(',
    'w ': 'return ',
    'w ': 'return ',
    'x ': 'return ',
    'x ': 'return ',
}

# 应用替换
decoded = packed_code
for old, new in replacements.items():
    decoded = decoded.replace(old, new)

print("=== 初步解码的代码 ===")
print(decoded)
