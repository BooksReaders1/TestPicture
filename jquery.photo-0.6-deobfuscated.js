/**
 * 完整解混淆后的图片处理代码
 * 包含: scramble_image_for_new, onImageLoadedForNew, get_num
 */

// ============================================
// get_num 函数 - 计算图片切片数量
// ============================================
function get_num(e, t) {
    var a = 10;
    // base64解码参数
    e = window.atob(e);
    t = window.atob(t);
    
    // 拼接后计算MD5
    var n = e + t;
    n = md5(n);
    n = n.substr(-1); // 取最后一位字符
    n = n.charCodeAt(); // 转为ASCII码
    
    // 根据e的值范围调整n
    var eInt = parseInt(e);
    if (eInt >= 268850 && eInt <= 421925) {
        n %= 10;
    } else if (eInt >= 421926) {
        n %= 8;
    }
    
    // 根据n的值返回切片数量 (2-20之间的偶数)
    switch (n) {
        case 0: a = 2; break;
        case 1: a = 4; break;
        case 2: a = 6; break;
        case 3: a = 8; break;
        case 4: a = 10; break;
        case 5: a = 12; break;
        case 6: a = 14; break;
        case 7: a = 16; break;
        case 8: a = 18; break;
        case 9: a = 20; break;
    }
    
    return a;
}

/**
 * 主函数：处理图片解混淆
 * @param {HTMLElement} e - 图片元素
 * @param {number|string} t - 最小高度阈值
 * @param {number|string} a - 最大高度阈值
 * @param {boolean} o - 是否强制重新加载
 * @param {boolean} d - 是否强制处理
 */
function scramble_image_for_new(e, t, a, o, d) {
    if (o || (o = false), d || (d = false), "true" === e.dataset.scrambleProcessed) {
        var r = $(e).next("canvas");
        if (r.length > 0 && r[0].width > 0) {
            return void console.log("圖片已正確處理，跳過:", e.id);
        }
        console.log("檢測到 canvas 丟失，重新處理:", e.id);
        e.dataset.scrambleProcessed = "false";
    }
    
    // 如果是 GIF 图片或高度在阈值范围内，直接显示原图
    if (e.src.indexOf(".gif") > 0 || parseInt(t) < parseInt(a) || "1" == d) {
        if ("none" === e.style.display) {
            e.style.display = "block";
        }
        return void (e.dataset.scrambleProcessed = "true");
    }
    
    // 等待图片加载完成或直接处理
    if (1 == o || 0 == e.complete) {
        e.onload = function() {
            onImageLoadedForNew(e);
        };
    } else {
        onImageLoadedForNew(e);
    }
}

/**
 * 图片加载完成后执行的解混淆处理
 * @param {HTMLElement} e - 图片元素
 */
function onImageLoadedForNew(e) {
    if ("true" !== e.dataset.scrambleProcessed) {
        var t, a = e.nextElementSibling, o;
        
        // 检查下一个元素是否是 canvas
        if (a && "CANVAS" === a.tagName) {
            o = (t = a).getContext("2d");
            o.clearRect(0, 0, t.width, t.height);
        } else {
            // 创建新的 canvas 元素
            t = document.createElement("canvas");
            t.style.display = "block";
            e.after(t);
        }
        
        var o = t.getContext("2d"),
            d = e.width,
            r = e.naturalWidth,
            s = e.naturalHeight;
        
        // 检查图片尺寸是否异常
        if (0 === r || 0 === s) {
            return console.warn("圖片尺寸異常，延遲處理:", e.id),
            void setTimeout(function() {
                e.dataset.scrambleProcessed || onImageLoadedForNew(e);
            }, 100);
        }
        
        // 设置 canvas 尺寸
        t.width = r;
        t.height = s;
        
        // 限制显示宽度
        if (d > e.parentNode.offsetWidth || 0 == d) {
            d = e.parentNode.offsetWidth;
        }
        t.style.width = d + "px";
        
        // 获取用于生成切片数量的标识符
        var n = e.parentNode.id || e.id;
        n = n.split(".")[0];
        
        var i, l = $(e).attr("data-chapter-aid") || aid;
        
        // 处理标识符
        if (n.includes("next")) {
            n = n.split("_").pop();
        }
        
        try {
            // 使用 base64 编码的标识符生成切片数量
            var c = get_num(window.btoa(l), window.btoa(n)),
                f = parseInt(s % c),  // 余数，用于处理不能整除的情况
                m = r,  // 切片宽度（使用原图宽度）
                g = 0;
            
            // 按行切片并重新排列
            for (; g < c; g++) {
                var h = Math.floor(s / c),  // 每片的高度
                    u = h * g,              // 源图像的起始 Y 坐标
                    p = s - h * (g + 1) - f; // 目标图像的起始 Y 坐标（反向排列）
                
                // 第一片需要加上余数
                if (0 == g) {
                    h += f;
                } else {
                    u += f;
                }
                
                // 将图片的一片绘制到 canvas 的另一个位置
                o.drawImage(e, 0, p, m, h, 0, u, m, h);
            }
            
            // 标记为已处理，隐藏原图
            e.dataset.scrambleProcessed = "true";
            $(e).addClass("hide");
            
        } catch (t) {
            console.error("圖片重組失敗:", t, e.id);
            e.style.display = "block";
            e.dataset.scrambleProcessed = "true";
        }
    }
}
