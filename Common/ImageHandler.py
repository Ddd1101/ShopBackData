"""图片缓存/下载/读取：与宿主回调解耦，不依赖 Qt。"""

import io
import os
import time
import urllib.request


def _image_name(url):
    return url.split('.jpg')[0].split('/')[-1]


def SaveImage(imageData, imageName, images_dir='images'):
    os.makedirs(images_dir, exist_ok=True)
    with open(os.path.join(images_dir, imageName + '.jpg'), 'wb') as f:
        f.write(imageData)


def IsImageExist(filename, images_dir='images'):
    return os.access(os.path.join(images_dir, filename + '.jpg'), os.R_OK)


def ReadImageFromDir(filename, images_dir='images'):
    with open(os.path.join(images_dir, filename + '.jpg'), 'rb') as f:
        return io.BytesIO(f.read())


def download_image(url, images_dir='images', check_cancel=None, logger=None, on_manual_download=None):
    """下载图片。

    依次尝试：requests 下载并保存 → urllib 读取 → 本地已有手动下载图片。
    全部失败时通过 on_manual_download(url) 回调宿主手动处理（如打开浏览器）。
    """

    import requests

    check_cancel = check_cancel or (lambda: None)
    _debug = logger.debug if logger is not None else (lambda *a, **k: None)

    # 尝试 1：requests 直接下载并保存
    try:
        check_cancel()
        time.sleep(0.3)
        resp = requests.get(url)
        if resp.status_code == 200:
            SaveImage(resp.content, _image_name(url), images_dir)
            return resp.content
        _debug('图片下载失败(status %s)', resp.status_code)
    except Exception as e:  # noqa: BLE001
        _debug('图片下载异常: %s', e)

    # 尝试 2：urllib 读取
    try:
        check_cancel()
        return urllib.request.urlopen(url).read()
    except Exception as e:  # noqa: BLE001
        _debug('图片获取异常: %s', e)

    # 兜底：本地已有手动下载的图片
    if IsImageExist(_image_name(url), images_dir):
        return ReadImageFromDir(_image_name(url), images_dir)

    # 兜底：通知宿主手动下载
    if on_manual_download is not None:
        on_manual_download(url)
        return None

    raise RuntimeError('图片下载失败: ' + url)