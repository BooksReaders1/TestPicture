import re
import json

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
print("=== 解压后的混淆代码 ===")
print(packed_code)
print("\n")

# 关键字数组（从 _0x4c12() 返回的数组索引 12 开始）
keywords_str = '||dataset|scrambleProcessed|var|if|id|true|width|style||function||||||||console|display||||||onImageLoadedForNew|||||canvas|return|void|parseInt|block|parentNode|next|log|getContext|2d|height|offsetWidth|split|aid|window|btoa|scramble_image_for_new|length|false|src|indexOf|gif|none|complete|onload|nextElementSibling|CANVAS|tagName|clearRect|else|document|createElement|after|naturalWidth|naturalHeight|warn|setTimeout|100|px|attr|data|chapter|includes|_|pop|try|for|get_num|Math|floor|drawImage|addClass|hide|catch|error'
keywords = keywords_str.split('|')

# 创建非空关键字到索引的映射
keyword_map = {}
for i, kw in enumerate(keywords):
    if kw:
        keyword_map[i] = kw

print("=== 关键字映射表 ===")
for idx, kw in sorted(keyword_map.items()):
    print(f"  {idx} -> '{kw}'")
print()

# 基数 62 编码/解码
BASE62_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def base62_encode(num):
    if num == 0:
        return BASE62_CHARS[0]
    result = ''
    while num > 0:
        result = BASE62_CHARS[num % 62] + result
        num //= 62
    return result

def find_all_base62_refs(code):
    """找到所有可能是 base62 编码的引用"""
    pattern = r'\b([0-9a-zA-Z]+)\b'
    matches = re.findall(pattern, code)
    # 过滤掉明显的关键字和单字符变量
    refs = set()
    for m in matches:
        if len(m) >= 1 and m not in ['e', 't', 'a', 'o', 'd', 'r', 'q', 'n', 'i', 'l', 'c', 'f', 'm', 'g', 'h', 'u', 'p', 's', 'x', 'y', 'j', 'J', 'Z', 'I', 'L', 'M', 'F', 'G', 'K', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'N', 'b', 'w']:
            try:
                val = int(m, 62) if not all(c in '0123456789' for c in m) else int(m)
                if val in keyword_map:
                    refs.add((m, val, keyword_map[val]))
            except:
                pass
    return refs

refs = find_all_base62_refs(packed_code)
print("=== 检测到的 base62 引用 ===")
for ref, val, kw in sorted(refs, key=lambda x: x[1]):
    print(f"  '{ref}' (base62={val}) -> '{kw}'")
