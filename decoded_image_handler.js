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

// ============================================
// onImageLoadedForNew 函数 - 图片加载完成后的处理
// ============================================
function onImageLoadedForNew(imgElement) {
    // 如果已经处理过，直接返回
    if (imgElement.dataset.scrambleProcessed === "true") {
        return;
    }
    
    var canvas, ctx;
    var parent = imgElement.parentNode;
    
    // 检查是否存在canvas元素
    if (parent && parent.tagName === "CANVAS") {
        canvas = parent;
        ctx = canvas.getContext("2d");
    } else {
        // 创建新的canvas元素
        canvas = document.createElement("canvas");
        canvas.style.display = "none";
        imgElement.parentNode.insertBefore(canvas, imgElement.nextSibling);
        
        ctx = canvas.getContext("2d");
        var width = imgElement.naturalWidth;
        var height = imgElement.naturalHeight;
        
        // 检查图片尺寸是否异常
        if (height === 0 || width === 0) {
            console.warn("图片尺寸异常，延迟处理:", imgElement.src);
            setTimeout(function() {
                if (!imgElement.dataset.scrambleProcessed) {
                    onImageLoadedForNew(imgElement);
                }
            }, 100);
            return;
        }
        
        canvas.width = width;
        canvas.height = height;
        
        // 设置canvas显示宽度（响应式）
        var displayWidth = imgElement.offsetWidth;
        if (displayWidth > width || displayWidth === 0) {
            displayWidth = width;
        }
        canvas.style.width = displayWidth + "px";
    }
    
    // 获取页面标识符用于计算切片数量
    var pageId = imgElement.dataset.chapterAid || imgElement.id || "";
    pageId = pageId.split(".")[0];
    
    // 获取下一个兄弟元素的id作为第二个参数
    var nextEl = imgElement.nextElementSibling;
    var nextId = "";
    if (nextEl && nextEl.id) {
        nextId = nextEl.id.split("_")[0];
    }
    
    try {
        // 计算切片数量
        var sliceCount = get_num(window.btoa(pageId), window.btoa(nextId));
        var remainder = height % sliceCount;
        var sliceHeight = Math.floor(height / sliceCount);
        var imgWidth = imgElement.naturalWidth;
        
        // 逐片反向绘制
        for (var i = 0; i < sliceCount; i++) {
            var h = Math.floor(height / sliceCount);
            var sourceY = height - h * (i + 1) - remainder;
            var destY = h * i;
            
            // 第一片需要加上余数
            if (i === 0) {
                h += remainder;
            } else {
                sourceY += remainder;
            }
            
            // 从原图底部开始取片，绘制到canvas顶部
            // 源: (0, sourceY, imgWidth, h)
            // 目标: (0, destY, imgWidth, h)
            ctx.drawImage(
                imgElement,
                0, sourceY, imgWidth, h,
                0, destY, imgWidth, h
            );
        }
        
        // 标记已处理并显示
        imgElement.dataset.scrambleProcessed = "true";
        $(imgElement).addClass("scramble_processed");
        $(imgElement).hide();
        $(canvas).show();
        
    } catch (error) {
        console.error("图片重組失败:", error, imgElement.src);
        canvas.style.display = "none";
        imgElement.dataset.scrambleProcessed = "true";
        imgElement.style.display = "block";
    }
}

// ============================================
// scramble_image_for_new 函数 - 主入口函数
// ============================================
function scramble_image_for_new(imgElement, param1, param2, forceProcess, isRetry) {
    // 默认参数
    forceProcess = forceProcess || false;
    isRetry = isRetry || false;
    
    // 检查是否已经是处理后的状态
    if (imgElement.dataset.scrambleProcessed === "true") {
        console.log("图片已正确处理，跳过:", imgElement.src);
        return;
    }
    
    // 检查是否为GIF或特殊情况，直接显示原图
    if (imgElement.src.indexOf(".gif") > 0 || 
        param1 < param2 || 
        isRetry === "1") {
        if (imgElement.style.display === "none") {
            imgElement.style.display = "block";
        }
        imgElement.dataset.scrambleProcessed = "true";
        return;
    }
    
    // 等待图片加载完成
    if (forceProcess === true || imgElement.complete === false) {
        imgElement.onload = function() {
            onImageLoadedForNew(imgElement);
        };
    } else {
        onImageLoadedForNew(imgElement);
    }
}

// ============================================
// 使用示例
// ============================================
/*
// 方式1: 直接调用单个图片
var img = document.querySelector("img.lazy_img");
scramble_image_for_new(img, 1, 0, false, false);

// 方式2: 批量处理所有未处理的图片
$(document).ready(function() {
    $(".lazy_img").each(function() {
        var img = this;
        if (img.dataset.scrambleProcessed !== "true") {
            // 参数说明:
            // img: 图片元素
            // 1, 0: 比较参数，通常传1和0
            // false: 是否强制处理
            // false: 是否是重试
            scramble_image_for_new(img, 1, 0, false, false);
        }
    });
});

// 方式3: 监听图片加载后自动处理
$("img.lazy_img").on("load", function() {
    scramble_image_for_new(this, 1, 0, false, false);
});
*/
