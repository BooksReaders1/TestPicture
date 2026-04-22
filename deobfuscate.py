# 解混淆脚本

# 首先还原 _0x4c12() 返回的数组
words = ['2124CfgcKq', '4eeIpdD', '3263889lPpkUu', '194210AZgeAv', '540344ChfFVr', 'replace', '80OBVNbX', '614630MwrzUX', '44502efLknj', '2157706sTctVJ', 'fromCharCode', 'split', '7345280QblNeM', '||dataset|scrambleProcessed|var|if|id|true|width|style||function||||||||console|display||||||onImageLoadedForNew|||||canvas|return|void|parseInt|block|parentNode|next|log|getContext|2d|height|offsetWidth|split|aid|window|btoa|scramble_image_for_new|length|false|src|indexOf|gif|none|complete|onload|nextElementSibling|CANVAS|tagName|clearRect|else|document|createElement|after|naturalWidth|naturalHeight|warn|setTimeout|100|px|attr|data|chapter|includes|_|pop|try|for|get_num|Math|floor|drawImage|addClass|hide|catch|error']

# 分隔符是 '|'
separator = '|'

# 从混淆字符串中提取关键字映射
packed_code = 'b\x20L(e,t,a,o,d){5(o||(o=!1),d||(d=!1),\x227\x22===e.2.3){4\x20r=$(e).B(\x22v\x22);5(r.M>0&&r[0].8>0)w\x20x\x20j.C(\x22圖片已正確處理，跳過:\x22,e.6);j.C(\x22檢測到v丟失，重新處理:\x22,e.6),e.2.3=\x22N\x22}5(e.O.P(\x22.Q\x22)>0||y(t)<y(a)||\x221\x22==d)w\x22R\x22===e.9.k&&(e.9.k=\x22z\x22),x(e.2.3=\x227\x22);1==o||0==e.S?e.T=b(){q(e)}:q(e)}b\x20q(e){5(\x227\x22!==e.2.3){4\x20t,a=e.U,o;5(a&&\x22V\x22===a.W)(o=(t=a).D(\x22E\x22)).X(0,0,t.8,t.F);Y(t=Z.10(\x22v\x22)).9.k=\x22z\x22,e.11(t);4\x20o=t.D(\x22E\x22),d=e.8,r=e.12,s=e.13;5(0===r||0===s)w\x20j.14(\x22圖片尺寸異常，延遲處理:\x22,e.6),x\x2015(b(){e.2.3||q(e)},16);t.8=r,t.F=s,(d>e.A.G||0==d)&&(d=e.A.G),t.9.8=d+\x2217\x22;4\x20n=e.A.6||e.6;n=n.H(\x22.\x22)[0];4\x20i,l=$(e).18(\x2219-1a-I\x22)||I;n.1b(\x22B\x22)&&(n=n.H(\x221c\x22).1d());1e{1f(4\x20c=1g(J.K(l),J.K(n)),f=y(s%c),m=r,g=0;g<c;g++){4\x20h=1h.1i(s/c),u=h*g,p=s-h*(g+1)-f;0==g?h+=f:u+=f,o.1j(e,0,p,m,h,0,u,m,h)}e.2.3=\x227\x22,$(e).1k(\x221l\x22)}1m(t){j.1n(\x22圖片重組失敗:\x22,t,e.6),e.9.k=\x22z\x22,e.2.3=\x227\x22}}}'

# 手动解码 - 根据 words 数组建立映射
# words 中从索引 12 开始是关键字列表（前面的是一些混淆用的字符串）
keywords_str = '||dataset|scrambleProcessed|var|if|id|true|width|style||function||||||||console|display||||||onImageLoadedForNew|||||canvas|return|void|parseInt|block|parentNode|next|log|getContext|2d|height|offsetWidth|split|aid|window|btoa|scramble_image_for_new|length|false|src|indexOf|gif|none|complete|onload|nextElementSibling|CANVAS|tagName|clearRect|else|document|createElement|after|naturalWidth|naturalHeight|warn|setTimeout|100|px|attr|data|chapter|includes|_|pop|try|for|get_num|Math|floor|drawImage|addClass|hide|catch|error'

keywords = keywords_str.split('|')

# 创建映射表 (数字 -> 关键字)
# 在 eval 混淆中，变量名被替换为数字（基数62编码）
# 我们需要反向解码 packed_code

print("Keywords list:")
for i, kw in enumerate(keywords):
    if kw:
        print(f"{i}: '{kw}'")
